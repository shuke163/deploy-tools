#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: loggers.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/06 15:42
@software:  Door
"""

import sys
import json
import datetime
import logging
import traceback
import socket
from datetime import datetime

from django.conf import settings

from kafka import KafkaProducer
from kafka import errors


class JsonFormatterBase(logging.Formatter):
    def __init__(self, tags=None, fqdn=False, *args, **kwargs):
        self.project_dict = settings.PROJECT_DICT[0]
        self.message_type = self.project_dict.get("name", None)
        self.project = self.project_dict.get("name", None)
        self.department = self.project_dict.get('department', None)
        self.team = self.project_dict.get('team', None)
        self.tags = tags if tags is not None else []

        if fqdn:
            self.host = socket.getfqdn()
        else:
            self.host = socket.gethostname()

    def get_extra_fields(self, record):
        skip_list = (
            "args", "asctime", "created", "exc_info", "exc_text", "filename", "id", "levelname", "levelno", "modele",
            "msecs", "message", "msg", "name", "pathname", "relativeCreated", "extra", "request", "server_time",
            "stack_info"
        )

        if sys.version_info < (3, 0):
            easy_types = (bool, dict, float, int, list, type(None))
        else:
            easy_types = (str, bool, dict, float, int, list, type(None))

        fields = {}

        for key, value in record.__dict__.items():
            if key not in skip_list:
                if isinstance(value, easy_types):
                    fields[key] = value
                else:
                    fields[key] = repr(value)
        fields["project"] = self.project
        fields["department"] = self.department
        fields["team"] = self.team
        fields["logtype"] = self.project
        fields["message_type"] = self.message_type
        fields["log_debug"] = settings.DEBUG

        return fields

    def get_debug_fields(self, record):
        fields = {
            "stack_trace": self.format_exception(record.exc_info),
            "lineno": record.lineno,
            "process": record.process,
            "thread_name": record.threadName,
        }

        # funcName was added in 2.5
        if not getattr(record, "funcName", None):
            fields["funcName"] = record.funcName

        # processName was added in 2.6
        if not getattr(record, "processName", None):
            fields["processName"] = record.processName

        return fields

    @classmethod
    def format_source(cls, message_type, host, path):
        return f"{message_type}://{host}/{path}"

    @classmethod
    def format_timestamp(cls, time):
        tstamp = datetime.utcfromtimestamp(time)
        return tstamp.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (tstamp.microsecond / 1000) + "Z"

    @classmethod
    def format_exception(cls, exc_info):
        return "".join(traceback.format_exception(*exc_info)) if exc_info else ""

    @classmethod
    def serialize(cls, message):
        return json.dumps(message)


class JsonFormatter(JsonFormatterBase):
    def format(self, record):
        message = {
            "@timestap": self.format_timestamp(record.created),
            "version": "v0.1",
            "messgae": record.getMessage(),
            "host": self.host,
            "pathname": record.pathname,
            "type": record.logtype,

            # Extra fields
            "level": record.levelname,
        }

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # if exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)


class KafkaLoggingHandler(logging.Handler, JsonFormatter):

    def __init__(self, brokers, topic, **kwargs):
        logging.Handler.__init__(self)
        self.topic = topic
        self.brokers = brokers
        try:
            self.producer = KafkaProducer(bootstrap_servers=brokers,
                                          value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        except:
            self.producer = None
        super(KafkaLoggingHandler).__init__()

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.producer:
                self.producer = KafkaProducer(bootstrap_servers=self.brokers,
                                              # value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                              compression_type='gzip')
                self.producer.send(self.topic, bytes(msg, encoding="utf-8"))
        except errors.NoBrokersAvailable:
            self.producer = None
        except Exception:
            self.handleError(record)

    def close(self):
        if self.producer is not None:
            self.producer.flush()
        logging.Handler.close(self)

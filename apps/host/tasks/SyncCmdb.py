#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: SyncCmdb.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/09 12:03
@software:  Door
"""

import os
import sys
import time
import logging
import subprocess
import traceback
from door.celery import app
from django.conf import settings
from apps.deploy import models
from utils.ansible_cmdb_api import AnsibleAPI

logger = logging.getLogger("door")


class TaskFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from celery._state import get_current_task
            self.get_current_task = get_current_task
        except ImportError:
            self.get_current_task = lambda: None

    def format(self, record):
        task = self.get_current_task()
        if task and task.request:
            record.__dict__.update(task_id=task.request.id,
                                   task_name=task.name)
        else:
            record.__dict__.setdefault('task_name', '')
            record.__dict__.setdefault('task_id', '')
        return super().format(record)


@app.task(name="tasks.cmdb")
def ansible_setup():
    try:
        business = models.BusinessLine.objects.filter(is_active=True).first()

        # update cmdb info
        inventory_ini = os.path.join("{BASE_DIR}/{business}/hosts.ini".format(BASE_DIR=settings.ANSIBLE["INVENTORY_PATH"], business=business))

        if inventory_ini:
            # result = AnsibleAPI(inventory_ini).cmdb()
            cmd = f"python {os.path.join(settings.BASE_DIR, 'utils/ansible_cmdb_api.py')}"
            proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            logger.info(f"Execute Pid: {proc.pid}")
            return {"result": "CMDB OK"}
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
        logger.error(f"{traceback.print_exc()}")
        logger.error(f"ansible setup module excute failed: {e}")


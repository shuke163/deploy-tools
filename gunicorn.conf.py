#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author: shuke
@Date: 2020-04-16 12:00:37
@LastEditTime: 2020-04-16 14:56:19
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /deploy-backend/gunicorn.conf.py
'''

import os
import logging
import logging.handlers
from pathlib import Path
from logging.handlers import WatchedFileHandler
import multiprocessing

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
var_dir = os.path.join(BASE_DIR, "var")

if not os.path.exists(var_dir):
    os.mkdir(var_dir)

threads = 2
workers = multiprocessing.cpu_count() * 2 + 1

bind = '0.0.0.0:8000'
backlog = 2048
chdir = BASE_DIR
timeout = 30
worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'

debug = True
daemon = True
loglevel = 'info'
proc_name = 'gunicorn.door-backend'
pidfile = os.path.join(BASE_DIR, "var/gunicorn.pid")

access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'

accesslog = os.path.join(BASE_DIR, "logs/gunicorn_access.log")
errorlog = os.path.join(BASE_DIR, "logs/gunicorn_error.log")

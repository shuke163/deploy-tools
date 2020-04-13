#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: celery.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/07 17:35
@software:  Door
"""

import os
import logging
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'door.settings')

app = Celery(settings.APP)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.broker_url = settings.CELERY['CELERY_BROKER_URL']
app.conf.result_backend = settings.CELERY['CELERY_RESULT_BACKEND_URL']

app.conf.timezone = 'Asia/Shanghai'
app.conf.enable_utc = False

# 有些情况可以防止死锁
app.conf.CELERYD_FORCE_EXECV = True
# 允许重试
app.conf.CELERY_ACKS_LATE = True
# 每个worker最多执行100个任务被销毁，可以防止内存泄漏
app.conf.CELERYD_MAX_TASKS_PER_CHILD = 100
# 软超时
app.conf.CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 60

# set celery msg format
app.conf.update(
    task_serializer='json',
    accept_content=['json', ],
    result_serializer='json',  # Ignore other content
    timezone=settings.CELERY['CELERY_TIMEZONE'],
    enable_utc=True
)

app.conf.beat_schedule = {
    'ansible-setup-task-per-minute': {
        'task': 'tasks.cmdb',  # 此处的task为设置的task的name名称
        'schedule': crontab(minute="*"),
        'args': (),
    },
}

# app.conf.beat_schedule = {
#     'ansible-playbook-task-per-minute': {
#         'task': 'tasks.ansible_playbook_api',  # 此处的task为设置的task的name名称
#         'schedule': crontab(minute="*/3"),
#         'args': (),
#     },
# }

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

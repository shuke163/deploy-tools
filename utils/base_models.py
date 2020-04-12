#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: base_models.py 
@time: 2019/10/25 13:26
@contact: zhaofengfeng@rongcloud.cn
@software:  Door
"""

from django.db import models


class BaseTimestampModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

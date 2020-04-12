# -*- coding: utf-8 -*-

from django.contrib.auth.models import AbstractUser
from django.db import models
from utils import base_models

from django.contrib.auth.models import AbstractUser


class Account(AbstractUser, base_models.BaseTimestampModel):
    """
    用户信息表
    """
    phone = models.CharField(max_length=11, null=True, blank=True, unique=True, verbose_name="phone")
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "weops_account"
        verbose_name = "用户表"
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.username

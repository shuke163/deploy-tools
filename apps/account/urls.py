#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: urls.py 
@time: 2019/10/25 19:11
@contact: shu_ke163@163.com
@software:  Door
"""

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from apps.account.views import *

router = DefaultRouter()
router.register(r'users', AccountViewSet, basename='user')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login$', LoginView.as_view()),
    url(r'^logout$', LogoutView.as_view()),
    url(r'^reset$', ResetPasswordView.as_view()),
]

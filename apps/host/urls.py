#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: urls.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/08 19:35
@software:  Door
"""
from django.conf.urls import url
from apps.host.views import HostView
from apps.host.views import HostGroupView
from apps.host.views import HostPushPortCheckListView
from apps.host.views import EnvCheckListView
from apps.host.views import SvcValidateListView

urlpatterns = [
    url(r'^host$', HostView.as_view(), name="host"),
    url(r'^svc_validate$', SvcValidateListView.as_view(), name="svc"),
    url(r'^check_push$', HostPushPortCheckListView.as_view(), name="push"),
    url(r'^host_group$', HostGroupView.as_view(), name="host_group"),
    url(r'^env_check$', EnvCheckListView.as_view(), name="env_check"),
    # url(r'^host_group/(?P<pk>[0-9]+)/$', HostGroupDetailView.as_view(), name="host_group-detail"),
]

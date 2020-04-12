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
from apps.deploy.views import PushResourceView
from apps.deploy.views import ServiceListView
from apps.deploy.views import BusinessListView
from apps.deploy.views import BusinessDetailView
from apps.deploy.views import ConfigMapListView
from apps.deploy.views import LicenseListView
from apps.deploy.views import SvcConfigView
from apps.deploy.views import DeployListView
from apps.deploy.views import CeleryResultListView
from apps.deploy.views import DownloadDeployLogListView

urlpatterns = [
    url(r'^config$', ConfigMapListView.as_view(), name="config"),
    url(r'^svc_config$', SvcConfigView.as_view(), name="svc_config"),
    url(r'^push_resource$', PushResourceView.as_view(), name="push_resource"),
    url(r'^service$', ServiceListView.as_view(), name="service"),
    url(r'^business$', BusinessListView.as_view(), name="business_list"),
    url(r'^business/(?P<pk>\d+)$', BusinessDetailView.as_view(), name="business_detail"),
    url(r'^license$', LicenseListView.as_view(), name="license"),
    url(r'^do_deploy$', DeployListView.as_view(), name="deploy"),
    url(r'^retry_deploy$', DeployListView.as_view(), name="retry_deploy"),
    url(r'^download_deploy_logs$', DownloadDeployLogListView.as_view(), name="download_logs"),
    url(r'^status$', CeleryResultListView.as_view(), name="status"),
    # url(r'^service/(?P<pk>[0-9]+)/$', ServiceView.as_view(), name="service-detail"),
]

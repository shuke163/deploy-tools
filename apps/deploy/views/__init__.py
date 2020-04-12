#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: __init__.py.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/09 10:55
@software:  Door
"""

from apps.deploy.views.ResourceView import PushResourceView
from apps.deploy.views.ServiceView import ServiceListView
from apps.deploy.views.ConfigView import ConfigMapListView
from apps.deploy.views.ConfigView import SvcConfigView
from apps.deploy.views.BusinessView import BusinessListView
from apps.deploy.views.BusinessView import BusinessDetailView
from apps.deploy.views.LicenseView import LicenseListView
from apps.deploy.views.DeployView import DeployListView
from apps.deploy.views.DeployView import CeleryResultListView
from apps.deploy.views.DownloadLogView import DownloadDeployLogListView

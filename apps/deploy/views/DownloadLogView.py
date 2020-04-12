#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: DownloadLogView.py 
@time: 2020/03/26 11:49
@contact: shu_ke163@163.com
@software:  Door
"""

import os
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404, StreamingHttpResponse

import logging

logger = logging.getLogger("door")


class DownloadDeployLogListView(generics.ListAPIView):
    """
    deploy logs
    """
    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    @swagger_auto_schema(operation_description='GET /api/v1/deploy/download_deploy_logs',
                         responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):

        try:
            log_path = settings.ANSIBLE["ANSIBLE_LOF_FILE"]
            if os.path.exists(log_path):
                response = StreamingHttpResponse(open(log_path, 'rb'))
                response['content_type'] = "application/octet-stream"
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(log_path)
                return response
            return Response({"code": status.HTTP_404_NOT_FOUND, "msg": "logs file not found!"})
        except Exception as e:
            raise Http404

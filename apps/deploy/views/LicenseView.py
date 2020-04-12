#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: LicenseView.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/05 09:06
@software:  Door
"""

from rest_framework.response import Response
from rest_framework import generics, status
from apps.deploy.serializers import LicenseSerializer
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.deploy import models
from utils.HandlerVars import ApplicationConfig
from django.db.models import Q


class LicenseListView(generics.ListAPIView):
    """
    license api view
    """
    queryset = models.ConfigMap.objects.all().order_by('-id')
    serializer_class = LicenseSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(Q(name__contains=search))
        else:
            queryset = queryset.filter(key="license")
        return queryset

    @swagger_auto_schema(operation_description='GET /api/v1/deploy/license',
                         responses={status.HTTP_200_OK: LicenseSerializer(many=True)})
    def get(self, request, *args, **kwargs):

        ser = LicenseSerializer(self.get_queryset(), many=True)

        return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": "ok"})

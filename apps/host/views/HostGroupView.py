#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: HostGroupView.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/19 12:59
@software:  Door
"""
from rest_framework.response import Response
from rest_framework import generics, status
from apps.host import models
from django.db.models import Q
from django.http import Http404
from apps.host.serializers import HostGroupSerializer
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.deploy.conf import ParseSvcSort

import logging

logger = logging.getLogger("door")


class HostGroupView(generics.ListCreateAPIView, generics.UpdateAPIView):
    """
    host group api view
    """
    queryset = models.HostGroup.objects.all().distinct().order_by('-id')
    serializer_class = HostGroupSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    @swagger_auto_schema(operation_description='GET /api/v1/host/host_group',
                         responses={status.HTTP_200_OK: HostGroupSerializer(many=True)})
    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(Q(name__contains=search))
        else:
            queryset = queryset.all().distinct().order_by('-id')
        return queryset

    def get_object(self, pk):
        try:
            return models.HostGroup.objects.get(pk=pk)
        except models.HostGroup.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        """
        初始化业务线对应的主机组
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        business = request.session.get("business", None)

        host_group_list = ParseSvcSort(business=business).host_group_list()

        for item in host_group_list:
            o, created = models.HostGroup.objects.get_or_create(**item)
            if created:
                logger.info(f"register host_group: {o.name} in business: {business}")

        ser = self.serializer_class(self.get_queryset(), many=True)
        return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": "ok"})

    @swagger_auto_schema(operation_description='POST /api/v1/host/host_group', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name", "description", "super_group"],
        properties={'name': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
                    'description': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
                    'super_group': openapi.Schema(type=openapi.TYPE_NUMBER, description='group_id number')}
    ), responses={status.HTTP_200_OK: HostGroupSerializer(many=True)})
    def post(self, request, *args, **kwargs):
        try:
            serializer_context = {
                'request': request,
            }

            ser = self.serializer_class(data=request.data, context=serializer_context)
            ser.is_valid(raise_exception=True)
            ser.save()

            return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": 'ok'})
        except Exception as e:
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

    @swagger_auto_schema(operation_description='PUT /api/v1/host/host_group', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["id"],
        properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer')}),
                         responses={status.HTTP_200_OK: f"update host_group success!"})
    def put(self, request, *args, **kwargs):
        id = request.data.get("id", None)
        svc = self.get_object(pk=id)
        ser = self.serializer_class(svc, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

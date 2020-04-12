#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: ServiceView.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/11 10:34
@software:  Door
"""
from django.conf import settings
from rest_framework.response import Response
from rest_framework import generics, status
from django.http import Http404
from apps.deploy import models
from apps.deploy.serializers import ServiceSerializer
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from apps.deploy.conf import ParseSvcSort
from drf_yasg import openapi

import logging

logger = logging.getLogger("door")


class ServiceListView(generics.ListCreateAPIView, generics.UpdateAPIView):
    """
    service api view
    """

    queryset = models.Service.objects.all().order_by("-id")
    serializer_class = ServiceSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("type", None)
        if search is not None:
            business_id = models.BusinessLine.objects.get(name=search).id
            queryset = queryset.filter(business_id=business_id).all().order_by("-id")
        else:
            queryset = models.Service.objects.all().order_by("-id")
        return queryset

    def get_object(self, pk):
        try:
            return models.Service.objects.get(pk=pk)
        except models.Service.DoesNotExist:
            raise Http404

    @swagger_auto_schema(operation_description='GET /api/v1/deploy/service',
                         responses={status.HTTP_200_OK: ServiceSerializer(many=True)})
    def get(self, request, *args, **kwargs):

        business = request.session.get("business", None)
        all_svc_list = ParseSvcSort(business).get_svc_list()

        for item in all_svc_list:
            item["business"] = models.BusinessLine.objects.get(name=item["business"])

            models.Service.objects.get_or_create(**item)

        ser = self.serializer_class(self.get_queryset(), many=True)

        return Response({"code": status.HTTP_200_OK, "result": ser.data, "msg": "ok"})

    @swagger_auto_schema(operation_description='POST /api/v1/deploy/service',
                         responses={status.HTTP_200_OK: f"post service success!"})
    def post(self, request, *args, **kwargs):
        try:
            ser = self.serializer_class(data=request.data)
            if ser.is_valid(raise_exception=True):
                ser.save()
                logger.info(f"Add service: {ser.data}")
                return Response({"code": status.HTTP_201_CREATED, "data": ser.data, "msg": 'ok'})
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"ServiceListView create service failed : {str(e)}")
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

    @swagger_auto_schema(operation_description='PUT /api/v1/deploy/service', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, properties={'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer')}),
                         responses={status.HTTP_201_CREATED: f"update service success!"})
    def put(self, request, pk, format=None):
        try:
            svc = self.get_object(pk)
            ser = self.serializer_class(svc, data=request.data)
            if ser.is_valid(raise_exception=True):
                ser.save()
                logger.info(f"update svc: {ser.data}")
                return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": "ok"})
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"ServiceListView update service failed: {str(e)}")
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

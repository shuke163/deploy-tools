#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: ResourceView.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/09 10:56
@software:  Door
"""

from rest_framework.response import Response
from rest_framework import generics, status
from apps.deploy.serializers import BusinessSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import NotFound
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.deploy import models
from utils.HandlerVars import ApplicationConfig
from utils.HandleExcel import ReadExcel
from django.db.models import Q

import logging

logger = logging.getLogger("door")


class BusinessListView(generics.ListCreateAPIView):
    """
    business api view
    """
    queryset = models.BusinessLine.objects.all().order_by('-id')
    serializer_class = BusinessSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(Q(name__contains=search))
        else:
            queryset = queryset.all().order_by('-id')
        return queryset

    @swagger_auto_schema(operation_description='GET /api/v1/deploy/business',
                         responses={status.HTTP_200_OK: BusinessSerializer(many=True)})
    def get(self, request, *args, **kwargs):

        business_list = ReadExcel(excel_name=request.session.get("excel_name", None)).get_business()

        # 初始化业务线
        for item in business_list:
            models.BusinessLine.objects.update_or_create(name=item["name"], defaults=item)

        ser = BusinessSerializer(self.get_queryset(), many=True)
        return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": "ok"})

    @swagger_auto_schema(operation_description='POST /api/v1/deploy/business', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name", "description"],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }), responses={status.HTTP_200_OK: BusinessSerializer(many=True)})
    def post(self, request, *args, **kwargs):
        try:
            serializer_context = {
                "name": request.data.get("name", None),
                "request": request
            }

            ser = self.serializer_class(data=request.data, context=serializer_context, )
            if ser.is_valid(raise_exception=True):
                ser.save()
                logger.info(f"Add business line is: {ser.data}")
                return Response({"code": status.HTTP_201_CREATED, "data": ser.data, "msg": 'ok'})
        except Exception as e:
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    business detail api
    """
    queryset = models.BusinessLine.objects.all().order_by('-id')
    serializer_class = BusinessSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    # lookup_field = 'name'
    #
    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(Q(name__contains=search))
        return queryset

    @swagger_auto_schema(operation_description='PUT /api/v1/deploy/business/{id}', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'name', 'is_active'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'is_active': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }), responses={status.HTTP_200_OK: BusinessSerializer(many=True)})
    def put(self, request, *args, **kwargs):
        try:

            serializer_context = {
                "id": request.data.get("id", None),
                "name": request.data.get("name", None),
                "is_active": request.data.get("is_active", None),
                "request": request
            }

            request.session["business"] = request.data.get("name", None)
            logger.info(f"set session key: business, value: {request.data.get('name', None)}")

            try:
                serializer_instance = self.get_object()
            except models.BusinessLine.DoesNotExist:
                raise NotFound("business dose not exists.")

            ser = self.serializer_class(serializer_instance, data=request.data, context=serializer_context,
                                        partial=True)
            if ser.is_valid(raise_exception=True):
                ser.save()
                logger.info(f"request args: {serializer_context}, update instance is: {ser.data}")
                return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": 'ok'})
        except Exception as e:
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

    @swagger_auto_schema(operation_description='PATCH /api/v1/deploy/business/{id}', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='bool'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }), responses={status.HTTP_201_CREATED: BusinessSerializer(many=True)})
    def patch(self, request, *args, **kwargs):
        try:
            serializer_context = {
                "id": request.data.get("id", None),
                "name": request.data.get("name", None),
                "is_active": request.data.get("is_active", None),
                "description": request.data.get("description", None),
                "request": request
            }

            try:
                serializer_instance = self.get_object()
            except models.BusinessLine.DoesNotExist:
                raise NotFound("business dose not exists.")

            logger.info(serializer_context)
            ser = self.serializer_class(serializer_instance, data=request.data, context=serializer_context,
                                        partial=True)
            if ser.is_valid(raise_exception=True):
                ser.save()
                logger.info(f"Update business line is: {ser.data}")
                return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": 'ok'})
        except Exception as e:
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

    @swagger_auto_schema(operation_description='DELETE /api/v1/deploy/business/{id}', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='integer'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }), responses={status.HTTP_204_NO_CONTENT: BusinessSerializer(many=True)})
    def delete(self, request, pk, *args, **kwargs):
        try:
            try:
                instance = self.get_object()
            except models.BusinessLine.DoesNotExist:
                raise NotFound("business dose not exists.")

            ser = self.get_serializer(instance)
            instance.delete()

            logger.info(f"delete business line is: {ser.data}")
            return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": 'ok'})
        except Exception as e:
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

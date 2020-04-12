#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: ConfigView.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/17 22:38
@software:  Door
"""

import sys
import traceback
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.generics import GenericAPIView
from apps.deploy.serializers import BusinessSerializer
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from utils.HandlerVars import ApplicationConfig
from utils.HandleExcel import ReadExcel
from drf_yasg import openapi
from apps.deploy import models
from django.db.models import Q

import logging

logger = logging.getLogger("door")


class SvcConfigView(generics.ListAPIView):
    """
    svc config view
    """

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    def get(self, request, *args, **kwargs):
        try:
            excel_name = request.session.get("excel_name", None)
            if not excel_name:
               raise Exception("Resource excel_name in session is None")

            global_vars_list = ReadExcel(excel_name=excel_name).get_all_global_vars
            if not global_vars_list:
                raise Exception("Parse global vars of sheet's content is None")
        
            #import json
            #print(json.dumps(global_vars[:-1], indent=4))            

            ret_config_list = []

            im_svc_list, rtc_svc_list = [], []
            for item in global_vars_list[:-1]:
                if item["key"] == "BASE_DIR":
                    ret_config_list.insert(0, {"title": "全局配置", "data": [item, ]})
                    continue
                elif item["key"] == "RCDB_NUM":
                    ret_config_list.insert(1, {"title": "RCDB(K/V 存储)", "data": [item, ]})
                    continue
                elif item["key"] == "FILE_PORT":
                    ret_config_list.insert(2, {"title": "文件服务器", "data": [item, ]})
                    continue
                elif item["business"] == "rcx" and not item["key"].startswith("RTC"):
                    im_svc_list.append(item)
                    continue
                elif item["business"] == "rtc":
                    rtc_svc_list.append(item)
                    continue
            # rcx service
            im_port_list = []
            for item in im_svc_list:
                for k, v in item.items():
                    if str(v).isdigit() and int(v) >= 1:
                        im_port_list.append(item)

            ret_config_list.insert(3 ,{"title": "IM 应用服务器", "data": im_port_list})
            ret_config_list.insert(4 ,{"title": "RTC 应用服务器", "data": rtc_svc_list})
          
            tpl = models.ConfigMap.objects.filter(title="template", key="template").values('value')
            logger.info(f"tpl: {tpl[0]['value']}")
            if tpl[0]['value'] == "local":
               tpl = 0
            else:
               tpl = 1

            rcdb_info = ret_config_list.pop(2)
            ret_config_list.insert(1, rcdb_info)
            
            res = {"type": tpl, "info": ret_config_list }

            return Response({"code": status.HTTP_200_OK, "result": res, "msg": "ok"})
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                             "msg": f'{e.__class__.__name__}: {e}'})

class ConfigMapListView(generics.ListCreateAPIView):
    """
    config api view
    """
    queryset = models.ConfigMap.objects.all().order_by('-id')
    serializer_class = BusinessSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(Q(name__contains=search))
        else:
            queryset = self.queryset.all().order_by("-id")
        return queryset

    @swagger_auto_schema(operation_description='GET /api/v1/deploy/config',
                         responses={status.HTTP_200_OK: f"get config info success!"})
    def get(self, request, *args, **kwargs):

        business = request.session.get("business", None)

        global_conf, bus_conf = ApplicationConfig(name="base").read, ApplicationConfig(name=business).read

        ret = dict()

        ret["global"] = global_conf.get("global", None)

        # global_mysql_list = global_conf.pop("mysql")
        # ret.setdefault("global", global_conf)
        # global_conf["isBase"] = True
        # global_conf["data"] = global_conf.pop("global")
        # global_conf["data"].extend(global_mysql_list)

        # ret.setdefault(business, bus_conf)

        del bus_conf["title"]
        del bus_conf["description"]
        del bus_conf["isBase"]

        for key, value in bus_conf.items():
            ret.setdefault(key, value)

        return Response({"code": status.HTTP_200_OK, "data": ret, "msg": "ok"})

    @swagger_auto_schema(operation_description='POST /api/v1/deploy/config', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, properties={
            'global': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'rcx_rcdb': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'rcx_server': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'rcx_fileserver': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'rcx_management': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'fastdfs': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'redis': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'nginx': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'zookeeper': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
            'mysql': openapi.Schema(type=openapi.TYPE_OBJECT, description='dict'),
        }), responses={status.HTTP_201_CREATED: f"update config info success!"})
    def post(self, request, *args, **kwargs):
        try:

            business = request.session.get("business", None)
            ApplicationConfig(business=business).write(request)

            return Response({"code": status.HTTP_201_CREATED, "data": None, "msg": 'ok'})
        except Exception as e:
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: ResourceView.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/09 10:56
@software:  Door
"""

import sys
import os
import traceback
from decimal import Decimal
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from apps.deploy import models
from apps.deploy.serializers import DeployModelsSerializer
from apps.host.views.HostView import AnsibleInventoryHosts
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from rest_framework.renderers import HTMLFormRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q

from utils.HandleExcel import ReadExcel

import logging

logger = logging.getLogger("door")


class ResourceHandlerExcel(object):

    def __init__(self, request):
        self.request = request
        self.excel = request.FILES.get("file", None)
        self.business_name = settings.DEFAULT_BUSINESS
        self.excel_path = os.path.join(settings.MEDIA_ROOT, self.excel.name.split('"')[0])
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)

    def handle_excel(self):
        """
        处理excel物料信息
        :return:
        """

        with open(self.excel_path, 'wb+') as excel_file:
            for chunk in self.excel.chunks():
                excel_file.write(chunk)

        if not self.excel.name.split('"')[0]:
            raise Exception("Resource excel name is None...")
       
        print(111111, self.request.session.__dict__["_session_cache"])

        for k in ["excel_name", "license"]:
            if k in self.request.session.__dict__["_session_cache"].keys():
                del self.request.session.__dict__["_session_cache"][k]
  
        self.request.session["excel_name"] = self.excel.name.split('"')[0]

        print(22222222, self.request.session.__dict__["_session_cache"])

        # business_list = ReadExcel(excel_name=self.excel.name.split('"')[0]).get_business()

        # 部署模型
        model_list = ReadExcel(excel_name=self.request.session["excel_name"]).parse_deploy_model()

        models.DeployModels.objects.all().delete()

        for item in model_list:
            mem = Decimal(item["mem"]).quantize(Decimal('0.00'))
            item["mem"] = mem
            obj = models.DeployModels.objects.create(**item)
            logger.info(f"insert deploy models: server_name: {obj.server_name}, private_ip: {obj.private_ip}, externalip: {obj.external_ip}, cpu: {obj.cpu}, mem: {obj.mem}, disk: {obj.disk}")

        # license以及配置信息
        license = str(self.request.data.get("license", None)).strip()
 
        if license:
            self.request.session["license"] = license
            logger.info(f"license info is: {license}")

        models.ConfigMap.objects.update_or_create(level="G", title="license", key="license",
                                             value=license, comment="license信息")
        server_name_list = []
        for item in model_list:
            server_name_list.append(item["server_name"])
        if settings.ANSIBLE["MYSQL_SLAVE_SERVER_NAME"] in server_name_list:
            tpl = "cluster"
        else:
            tpl = "local"

        c, created = models.ConfigMap.objects.update_or_create(level="G", key="template",
                                                          defaults={"level": "G", "title": "template",
                                                                    "key": "template", "value": tpl,
                                                                    "comment": "部署模型"})
        if c:
             logger.info(f"deploy host arch is: {tpl}")

        all_global_vars = ReadExcel(excel_name=self.excel.name.split('"')[0]).get_all_global_vars
        for conf in all_global_vars[:-1]:
            c, created = models.ConfigMap.objects.update_or_create(level="G", key=str(conf["key"]).lower(),
                                                          defaults={"level": "G", "title": conf["key"], "business": conf["business"],
                                                                    "key": str(conf["key"]).lower(), "value": conf["value"],
                                                                    "comment": conf["comment"]})
            #if c:
            #    logger.info(f"ConfigMap info: {conf}")

        # update business
        business_list = ReadExcel(excel_name=self.excel.name.split('"')[0]).get_business()
    
        s = sorted(business_list, key=lambda x: x['sort'], reverse=False)
        models.BusinessLine.objects.all().delete()
        for bus in business_list:
            bus["is_active"] = True
            models.BusinessLine.objects.create(**bus)

        business_dict = {}
        all_bus = models.BusinessLine.objects.filter().all()
        for bus in all_bus:
            business_dict[str(bus.name).lower()] = bus.sort 
       
        #self.request.session["business"] = str(obj.name).lower()

        logger.info(f"Business info is: {business_dict}")

        return model_list

class PushResourceView(generics.ListCreateAPIView, ResourceHandlerExcel):
    """
    push resource api view
    """
    queryset = models.DeployModels.objects.all().order_by('-id')
    serializer_class = DeployModelsSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer, HTMLFormRenderer)

    file_param = openapi.Parameter('file', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, description="file")

    license_param = openapi.Parameter('license', in_=openapi.IN_BODY, type=openapi.TYPE_STRING, description="string")

    # template_param = openapi.Parameter('template', in_=openapi.IN_BODY, type=openapi.TYPE_STRING, description="string")

    # response = openapi.Response('resource list', ResourceSerializer(many=True))

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(Q(name__contains=search))
        else:
            queryset = queryset.all().order_by('-id')
        return queryset

    @swagger_auto_schema(operation_description='POST /api/v1/deploy/push_resource',
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['file', ],
                             properties={
                                 'file': openapi.Schema(type=openapi.TYPE_FILE, in_=openapi.IN_FORM,
                                                        description="ExcelFile"),
                                 'license': openapi.Schema(type=openapi.TYPE_STRING, in_=openapi.IN_FORM,
                                                           description='string'),
                                 # 'template': openapi.Schema(type=openapi.TYPE_STRING, in_=openapi.IN_BODY,
                                 #                            description='string'),
                             }), responses={status.HTTP_200_OK: DeployModelsSerializer(many=True)})
    def post(self, request, *args, pk=None, **kwargs):
        try:
            excel = request.FILES.get("file")
            license = request.data.get("license")
        except KeyError as e:
            return Response({"code": status.HTTP_400_BAD_REQUEST, "msg": f"{e.__class__.__name__}: request parameter error, {str(e)}"})
        else:
            try:
                ResourceHandlerExcel(request).handle_excel()
                ser = DeployModelsSerializer(self.get_queryset(), many=True)
                return Response({"code": status.HTTP_200_OK, "result": ser.data, "msg": 'ok'})
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
                logger.error(f"{traceback.print_exc()}")
                return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})


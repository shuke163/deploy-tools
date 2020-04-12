#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: PortCheck.py 
@time: 2020/03/23 21:07
@contact: shu_ke163@163.com
@software:  Door
"""

import sys
import os
import socket
import traceback
import pandas as pd
import select
import socketserver
from operator import itemgetter
from rest_framework.response import Response
from rest_framework import generics, status
from apps.host import models
from apps.deploy.models import ConfigMap
from apps.deploy.models import BusinessLine
from apps.deploy.models import DeployModels
from django.conf import settings
from utils.HandleExcel import ReadExcel
from utils.ansible_cmdb_api import AnsibleAPI
from apps.host.serializers import HostSerializer
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404

import logging

logger = logging.getLogger("door")


class HostPushPortCheckListView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
    """
    push port check
    """

    queryset = models.Host.objects.all().order_by('-id')
    serializer_class = HostSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("type", None)
        if search is not None:
            business_id = models.Host.objects.get(name=search).id
            queryset = queryset.filter(business_id=business_id).all().order_by("-id")
        else:
            queryset = models.Host.objects.all().order_by("-id")
        return queryset

    def get_object(self, pk):
        try:
            return models.Host.objects.get(pk=pk)
        except models.Host.DoesNotExist:
            raise Http404

    @swagger_auto_schema(operation_description='GET /api/v1/host/check_push',
                         responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):
        channel, response = None, {}
        try:
            # listen mutil ports
            # self.listen_mutil_port(request)

            tpl = ConfigMap.objects.filter(title="template", key="template").first().value
            if tpl == "local":
               hostname =  DeployModels.objects.filter(business="rcx").first().hostname

            excel_name = request.session.get("excel_name", None)
            if not excel_name:
                raise Exception("Resource excel name is None")
            all_global_vars_list = ReadExcel(excel_name=excel_name).get_all_global_vars
            push_list = []
            for item in all_global_vars_list:
                if item["key"].endswith("PUSH"):
                    push_list.append({item["key"].split("_")[0]: item["value"]})

            logger.info(f"Parse resource excel, Get push list: {push_list}")

            response["hostname"] = hostname
            push_port_dict = settings.PUSH_ADDRESS

            push_dict = {}
            for push in push_list:
                for channel, switch in push.items():
                    if int(switch) == 1:
                        push_dict.update({channel: push_port_dict[channel]})
                    else:
                        # response.setdefault("result", {}).update({channel: False})
                        logger.info(f"{channel} is not open!")
           
            logger.info(f"push info: {push_dict}") 
            for channel, port_list in push_dict.items():
                
                status_list = []
                for port in port_list:
                    addr, port = port.split(":")

                    if int(port) > 65536:
                        logger.error(f"port don't allow to be greater than 65535")
                    else:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(10)

                        address = (str(addr), int(port))
                        result = s.connect_ex((address))
                        s.shutdown(2)
                        s.close()

                        if result == 0:
                            logger.info(f"check push channel: {channel}, addr: {addr}, port: {port}, status is open")
                        else:
                            logger.error(f"check push channel: {channel}, addr: {addr}, port: {port}, status is failed!")

                        status_list.append(result)

                if not any(status_list):
                    response.setdefault("result", {}).update({channel: True})
                else:
                    response.setdefault("result", {}).update({channel: False})

            result = [response, ]
            return Response({"code": status.HTTP_200_OK, "result": result, "msg": "ok"})
        except socket.error as e:
            exe_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            response.setdefault("result", {}).update({channel: False})
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

    def kill_listen_port_scripts_pid(self,):
        try:
            cmd = "ps -ef | grep listen_ports.py | grep -v grep  | awk '{print $2}'"
            out = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            infos = out.stdout.read().splitlines()
            if infos:
                spid = infos[0]
                pid = int(spid.decode())
                ret = os.kill(pid, signal.SIGKILL)
                logger.info(f"Has killed the pid of {pid} the process, return is : {ret}")
        except OSError as  e:
            logger.error(f"process not exist")


    def listen_mutil_port(self, listen_port_list=None):
        """
        listen ports
        """
        try:
            if not listen_port_list:
                raise Exception("port list is None")

            # with open(os.path.join(settings.BASE_DIR, "config/ports.json"), 'w', encoding="utf-8") as p:
            #     json.dump(listen_port_list, p, ensure_ascii=False)

            cmd = f"python {os.path.join(settings.BASE_DIR, 'utils/listen_ports.py')}"
            logger.info(f"cmd: {cmd}")
            proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
            logger.info(f"Execute listen port scripts Pid: {proc.pid}")

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")


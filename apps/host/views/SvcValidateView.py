#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: SvcValidateView.py
@time: 2020/03/24 20:09
@contact: shu_ke163@163.com
@software:  Door
"""

import sys
import json
import copy
import traceback
from django.conf import settings
from xmlrpc.client import ServerProxy
from supervisor.xmlrpc import SupervisorTransport
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from apps.host import models 
from apps.deploy.models import DeployModels
from apps.deploy.models import ConfigMap
from apps.host.serializers import SvcValidateModelsSerializer

import logging

logger = logging.getLogger("door")


class SvcValidateListView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
    """
    host api view
    """
    queryset = models.SvcValidateModel.objects.all().order_by('-id')

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    serializer_class = SvcValidateModelsSerializer

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("svc_name", None)
        if search is not None:
            models.SvcValidateModel.objects.filter(server_name=search).order_by("-id")
        else:
            queryset = models.SvcValidateModel.objects.all().order_by("-id")
        return queryset

    def get_object(self, pk):
        try:
            return models.SvcValidateModel.objects.get(pk=pk)
        except models.SvcValidateModel.DoesNotExist:
            raise Http404

    @swagger_auto_schema(operation_description='GET /api/v1/host/svc_validate',
                         responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):
        try:
            flag, msg = self._rpc_info()
            if flag:
                ser = SvcValidateModelsSerializer(self.get_queryset(), many=True)
                rcx_mgt_url = self._rcx_mgt_url()
                res = {"url": rcx_mgt_url, "info": ser.data}
                return Response({"code": status.HTTP_200_OK, "result": res, "msg": msg})
            else:
                return Response({'code': status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": msg})
        except Exception as e:
            return Response({'code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'msg': f'{e.__class__.__name__}: {e}'})

    def _rpc_info(self):
        """
        supervior rpc api for process info
        """
        try:
            addr = DeployModels.objects.filter(business="rcx").first().private_ip
            port, username, password = settings.SUPERVISOR["port"], settings.SUPERVISOR["username"], \
                                       settings.SUPERVISOR[
                                           "password"]

            rpc_address = "http://{addr}:{port}".format(addr=addr, port=port)

            transport = SupervisorTransport(username, password, rpc_address)
            server = ServerProxy(rpc_address, transport)
            supervisor_process_list = server.supervisor.getAllProcessInfo()

            all_hosts_list, deploy_host_list = DeployModels.objects.all().values("server_name", "hostname",
                                                                                        "business", "private_ip",
                                                                                        "external_ip",
                                                                                        "instance_name"), []
            for host in all_hosts_list:
                inst_list = str(host["instance_name"]).split(",")
                for ins in inst_list:
                    host["instance_name"] = ins
                    d = copy.deepcopy(host)
                    d["instance_name"] = host["instance_name"]
                    deploy_host_list.append(d)

            all_svc_list = []
            for host in deploy_host_list:
                for svc in supervisor_process_list:
                    if host["instance_name"] == svc["name"]:
                        svc["server_name"] = host["server_name"]
                        svc["hostname"] = host["hostname"]
                        svc["business"] = host["business"]
                        svc["private_ip"] = host["private_ip"]
                        svc["external_ip"] = host["external_ip"]
                        svc["instance_name"] = host["instance_name"]
                        all_svc_list.append(svc)
            
            logger.info(f"supervisor rpc process info: -> {json.dumps(all_svc_list, indent=4, ensure_ascii=False)}")

            models.SvcValidateModel.objects.all().delete()
            for svc in all_svc_list:
                models.SvcValidateModel.objects.create(**svc)

            return True, "ok"

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            return False, f"{traceback.format_exception(exc_type, exc_value, exc_traceback)[-1]}"

    def _rcx_mgt_url(self):
        """
        rcx mgt url
        """
        private_ip = DeployModels.objects.filter(business="rcx").first().private_ip
        mgt_port = ConfigMap.objects.filter(business="rcx", title="RCX_MGT", key="rcx_mgt").first().value 
        rcx_mgt_url = f"http://{private_ip}:{mgt_port}/management"
        logger.info(f"rcx management url: {rcx_mgt_url}")
        return rcx_mgt_url


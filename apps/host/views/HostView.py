#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: HostView.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/19 12:58
@software:  Door
"""

import os
import re
import configparser
from ruamel import yaml
from rest_framework.response import Response
from rest_framework import generics, status
from apps.host import models
from apps.deploy.models import DeployModels
from django.conf import settings
from apps.host.serializers import HostSerializer
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import Http404
from utils.HandleExcel import ReadExcel

import logging

logger = logging.getLogger("door")

yml = yaml.YAML()
yml.indent(mapping=2, sequence=4, offset=2)


class HostView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
    """
    host api view
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

    @swagger_auto_schema(operation_description='GET /api/v1/host/host',
                         responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):
        #try:
        host_info_dict = AnsibleInventoryHosts(request).write_inventory_host()

        response = []
        # 更新deploy_models表
        for row in host_info_dict["all"]:
            if row["server_name"] == "rtc_server":
                row["business"] = "rtc"
            else:
                row["business"] = "rcx"
              
            response.append(row)

            DeployModels.objects.filter(server_name=row["server_name"], private_ip=row["private_ip"]).update(
                server_name=row["server_name"], hostname=row["hostname"], private_ip=row["private_ip"],
                external_ip=row["external_ip"], business=row["business"], cpu=str(int(row["cpu"])) + "c",
                mem=str(int(row["mem"])) + " GB", disk="%.02f GB" % float(row["disk"]),
                instance_name=",".join(row["instance_name"]),
                description=row["description"]
            )

        
        return Response({"code": status.HTTP_200_OK, "result": response, "msg": "ok"})
        #except Exception as e:
        #    print(e)
        #    return Response(
        #        {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

    # @swagger_auto_schema(operation_description='POST /api/v1/host/host', request_body=openapi.Schema(
    #     type=openapi.TYPE_OBJECT,
    #     required=["hostname", "private_ip", "public_ip", "user", "password", "private_key_file", "host_group"],
    #     properties={
    #         'hostname': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    #         'private_ip': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    #         'public_ip': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    #         'user': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    #         'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    #         'private_key_file': openapi.Schema(type=openapi.TYPE_FILE, description='file'),
    #         'host_group': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.TYPE_ARRAY, description='array'),
    #     }
    # ), responses={status.HTTP_200_OK: HostSerializer(many=True)})
    # def post(self, request, *args, **kwargs):
    #
    #     AnsibleInventoryHosts(request).host_group()
    #
    #     try:
    #         serializer_context = {
    #             "group": request.data["host_group"],
    #             "request": request,
    #         }
    #         logger.info(f"host info: {request.data}")
    #         ser = self.serializer_class(data=request.data, context=serializer_context)
    #         if ser.is_valid(raise_exception=True):
    #             ser.save()
    #             logger.info(f"Add host info: {ser.data}")
    #             return Response({"code": status.HTTP_200_OK, "data": ser.data, "msg": 'ok'})
    #     except Exception as e:
    #         return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})


class AnsibleInventoryHosts(object):
    """
    处理host接口上传的主机信息
    """

    def __init__(self, request):
        self.business = request.session.get("business", None)
        self.excel_name = request.session.get("excel_name", None)
        self.model_list = ReadExcel(excel_name=self.excel_name).parse_deploy_model()
        self.ansible_host_info_dict = self.host_info_dict()
        self.ansible_inventory_path = os.path.join(settings.ANSIBLE["INVENTORY_PATH"])
        self.host_path = os.path.join(self.ansible_inventory_path, 'hosts.ini')
        logger.info(f"update ansible inventory host file: {self.host_path}")

    @property
    def get_rcdb_num(self):

        all_global_vars_list = ReadExcel(excel_name=self.excel_name).get_all_global_vars
        for item in all_global_vars_list:
            if item["key"] == settings.RCDB_DICT["RCDB_NUM_KEY"]:
                value = int(item["value"])
                return value

    @property
    def host_group(self):
        self.host_group_list = ["all", settings.ANSIBLE["MYSQL_GROUP_NAME"]]
        for item in self.model_list:
            self.host_group_list.append(item["server_name"])

        for group in list(set(self.host_group_list)):
            if re.search(f'\w+_{settings.ANSIBLE["MYSQL_GROUP_NAME"]}_\w+', group):
                self.host_group_list.remove(group)

        return list(set(self.host_group_list))

    def host_info_dict(self):

        host_group_dict = {}
        for group_name in self.host_group:
            for row in self.model_list:
                if group_name == row["server_name"]:
                    host_group_dict.setdefault(group_name, []).append(row)
                elif re.search('\w+_mysql_\w+', f'{row["server_name"]}') and group_name == settings.ANSIBLE[
                    "MYSQL_GROUP_NAME"]:
                    host_group_dict.setdefault(settings.ANSIBLE["MYSQL_GROUP_NAME"], []).append(row)

        all_host_list, instance_list = [], []
        for group_name, host_list in host_group_dict.items():
            if group_name == settings.RCDB_DICT["RCDB_GROUP_NAME"]:
                for i in range(self.get_rcdb_num):
                    instance_list.append(f'{group_name}.inst-{i}')

                for host in host_list:
                    host["business"] = self.business
                    host["hostname"] = f'{group_name}_node0{host_list.index(host) + 1}'
                    host["instance_name"] = instance_list
                continue

            if len(host_list) > 1 and group_name != settings.RCDB_DICT["RCDB_GROUP_NAME"]:
                for host in host_list:
                    host["business"] = self.business
                    host["hostname"] = f'{group_name}_node0{host_list.index(host) + 1}'
                    host["instance_name"] = [f'{group_name}.inst-0', ]
            else:
                host_list[0]["business"] = self.business
                host_list[0]["hostname"] = f'{group_name}_node01'
                host_list[0]["instance_name"] = [f'{group_name}.inst-0', ]

            all_host_list.append(host_list)

        for item in all_host_list:
            for host in item:
                host_group_dict.setdefault("all", []).append(host)

        host_group_dict["all"].extend(host_group_dict[settings.RCDB_DICT["RCDB_GROUP_NAME"]])

        logger.info(f"host info dict: {host_group_dict}")

        return host_group_dict

    def write_inventory_host(self):
        try:

            if not os.path.exists(self.ansible_inventory_path):
                os.makedirs(os.path.join(self.ansible_inventory_path, f"group_vars"))
                os.makedirs(os.path.join(self.ansible_inventory_path, f"host_vars"))

            self.write_ansible_vars()

            config = configparser.ConfigParser()
            for section in sorted(self.host_group):
                config.add_section(section=section)

            for group, host_list in self.ansible_host_info_dict.items():

                for host in host_list:
                    if group == "all":
                        if not host["external_ip"]:
                            config.set(group, host["hostname"],
                                       f"\t\tprivate_ip={host['private_ip']}\t\tansible_host={host['private_ip']}\t\tansible_user={settings.ANSIBLE['ANSIBLE_USER']}\t\tansible_connection=local")
                        else:
                            config.set(group, host["hostname"],
                                       f"\t\tprivate_ip={host['private_ip']}\t\tansible_host={host['private_ip']}\t\tansible_user={settings.ANSIBLE['ANSIBLE_USER']}\t\tpublic_ip={host['external_ip']}\t\tansible_connection=local")
                    elif group == settings.ANSIBLE["MYSQL_GROUP_NAME"]:
                        if re.search('\w+_mysql_master', f'{host["server_name"]}'):
                            config.set(group, host["hostname"],
                                       "\t\tmysql_server_id=1\t\tmysql_replication_role=master")
                        elif re.search('\w+_mysql_slave', f'{host["server_name"]}'):
                            config.set(group, host["hostname"],
                                       "\t\tmysql_server_id=2\t\tmysql_replication_role=slave")
                        else:
                            config.set(group, host["hostname"],
                                       "\t\tmysql_server_id=1\t\tmysql_replication_role=master")
                    else:
                        config.set(group, host['hostname'], f"")

            if os.path.exists(self.host_path):
                os.remove(self.host_path)
            config.write(open(self.host_path, "w"))

            host_ini_list = list()
            with open(self.host_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if "=" in line:
                        row_list = [str(line.split("=", 1)[0]).strip(), str(line.split("=", 1)[1]).replace(" ", "")]
                        host_ini_list.append("".join(row_list))
                    else:
                        host_ini_list.append(line)

            with open(self.host_path, 'w', encoding="utf-8") as h:
                h.writelines(host_ini_list)

            # logger.info(f"ansible inventory host: {host_ini_list}")

            return self.host_info_dict()

        except configparser.DuplicateSectionError as e:
            logger.error(f"handler ansible inventory file failed!")

    def write_ansible_vars(self):
        for group in self.host_group:
            with open(os.path.join(self.ansible_inventory_path, f"group_vars/{group}.yml"), "w",
                      encoding="utf-8") as f:
                f.write("")
        for host in self.ansible_host_info_dict["all"]:
            with open(os.path.join(self.ansible_inventory_path, f"host_vars/{host['hostname']}.yml"), "w",
                      encoding="utf-8") as f:
                f.write("")

        all_global_vars_list = ReadExcel(excel_name=self.excel_name).get_all_global_vars

        group_all_vars_dict = {}
        for item in all_global_vars_list[:-1]:
            if item["key"] == "BASE_DIR":
                group_all_vars_dict[item["key"]] = item["value"]
                continue

            group_all_vars_dict.setdefault(item["business"], []).append(
                    {item["key"].strip(): str(item["value"]).strip()})
            
            logger.info(f"{item['business']}: {item['key']} {item['value']}")

        logger.info(f"anisble group all.yml content: {group_all_vars_dict}")

        # all.yml
        with open(os.path.join(self.ansible_inventory_path, f"group_vars/all.yml"), "w", encoding="utf-8") as f:
            yaml.round_trip_dump(group_all_vars_dict, f, default_flow_style=False, allow_unicode=True, indent=2,
                                 block_seq_indent=2)

        
        # rcx_server.yml
        group_all_vars_dict.pop("BASE_DIR")

        rcx_conf_dict = {}
        rcx_conf_dict["rcx_conf"] = group_all_vars_dict.pop("rcx")

        for item in rcx_conf_dict["rcx_conf"]:
            for k, v in item.items():
                if k == settings.RCDB_DICT["RCDB_NUM_KEY"]:
                    rcx_conf_dict["rcx_conf"].remove(item)
                elif str(k) == "RCX_MGT":
                    rcx_conf_dict["rcx_conf"].remove(item)
       
        push_list, rcx_conf_list = [], []
        for item in rcx_conf_dict["rcx_conf"]:
            for k, v in item.items():
                if k.endswith("PUSH"):
                    push_list.append(item)
                else:
                    rcx_conf_list.append(item)

        rcx_conf_dict["push"] = push_list
        rcx_conf_dict["rcx_conf"] = rcx_conf_list

        with open(os.path.join(self.ansible_inventory_path, f"group_vars/rcx_server.yml"), "w", encoding="utf-8") as f:
            yaml.round_trip_dump(rcx_conf_dict, f, default_flow_style=False, allow_unicode=True, indent=2,
                                 block_seq_indent=2)

        # rtc_server.yml
        rtc_conf_dict = {}
        rtc_conf_dict["rtc_conf"] = group_all_vars_dict.pop("rtc")
        with open(os.path.join(self.ansible_inventory_path, f"group_vars/rtc_server.yml"), "w", encoding="utf-8") as f:
            yaml.round_trip_dump(rtc_conf_dict, f, default_flow_style=False, allow_unicode=True, indent=2,
                                 block_seq_indent=2)
         
                

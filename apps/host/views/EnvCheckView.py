#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: EnvCheckView.py
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/08 17:44
@software: door backend
"""

import os
import sys
import json
import signal
import socket
import psutil
import traceback
import pandas as pd
import socketserver
import subprocess
import select
from decimal import Decimal
from operator import itemgetter
from ruamel import yaml
from multiprocessing import Process
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from apps.deploy import models
from apps.host.models import Cmdb
from utils.ansible_cmdb_api import AnsibleAPI
from utils.HandleExcel import ReadExcel

import logging

logger = logging.getLogger("door")

yml = yaml.YAML()
yml.indent(mapping=2, sequence=4, offset=2)

class EnvCheckListView(generics.ListAPIView):
    """
    env check view
    """

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    ret_list = []

    @swagger_auto_schema(operation_description='GET /api/v1/host/env_check', responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):

        distinct_listen_port_list = self.handler_port()

        if self.ret_list:
            self.ret_list = []

        try:
            # kill listen port scripts
            self.kill_listen_port_scripts_pid()

            host_list = models.DeployModels.objects.filter().all()

            # get cmdb info
            flag, result = self.get_cmdb_info()
            if flag and result["success"]:
                logger.info(f"Get cmdb info success, Through ansible setup module!")
            elif flag and result["failed"]:
                logger.error(f"Execute the ansible api failed, msg: {result['failed']}")
                raise Exception("Execute the ansible api failed, {msg}".format(msg=result["failed"]))
            else:
                inventory_ini = os.path.join("{BASE_DIR}/hosts.ini".format(BASE_DIR=settings.ANSIBLE["INVENTORY_PATH"],))
                logger.error(f"Execute the ansible setup api failed, please check {inventory_ini} file.")
                raise Exception(f"Execute the ansible setup api failed, please check {inventory_ini} file.")

            ansible_setup_host_list = Cmdb.objects.filter().all()
            if not ansible_setup_host_list:
                raise Exception("cmdb table no data!")

            disk = self.max_disk_space

            for host in host_list:
                logger.info(f"env check hostname: {host.hostname}, private_ip: {host.private_ip}")

                host_check_dict = {}
                for item in ansible_setup_host_list:
                    if host.hostname == item.hostname:
                        host_check_dict.setdefault("hostname", host.hostname)
                        host_check_dict.setdefault("external_ip", host.external_ip)
                        host_check_dict.setdefault("result", {}).update({"os": {"expect": settings.OS_VERSION, "fact": f"{item.os_type} {item.os_version}"}})
                        host_check_dict.setdefault("result", {}).update({"cpu": {"expect": host.cpu, "fact": item.cpu}})
                        host_check_dict.setdefault("result", {}).update({"memory": {"expect": host.mem, "fact": item.memory}})
                        host_check_dict.setdefault("result", {}).update({"disk": {"expect": disk, "fact": item.disk}})
                        host_check_dict.setdefault("result", {}).update({"disk_format": {"expect": "ext4", "fact": item.disk_format}})
                        host_check_dict.setdefault("result", {}).update({"ports": {"expect": distinct_listen_port_list, "fact": []}})

                        # os
                        expect_os_list = str(host_check_dict["result"]["os"]["expect"]).split()
                        fact_os_list = str(host_check_dict["result"]["os"]["fact"]).split()
                        if expect_os_list[0] == fact_os_list[0] and fact_os_list[1] > expect_os_list[1]:
                            host_check_dict["result"]["os"]["status"] = True
                        elif expect_os_list[0] == fact_os_list[0] and fact_os_list[1] == expect_os_list[1]:
                            host_check_dict["result"]["os"]["status"] = True
                        else:
                            host_check_dict["result"]["os"]["status"] = False

                        # cpu
                        expect_cpu = int(list(host_check_dict["result"]["cpu"]["expect"])[0])
                        fact_cpu = int(list(host_check_dict["result"]["cpu"]["fact"])[0])
                        if fact_cpu >= expect_cpu:
                            host_check_dict["result"]["cpu"]["status"] = True
                        else:
                            host_check_dict["result"]["cpu"]["status"] = False

                        # mem
                        expect_mem_list = str(host_check_dict["result"]["memory"]["expect"]).split()
                        fact_mem_list = str(host_check_dict["result"]["memory"]["fact"]).split()
                        mem = Decimal(str(host_check_dict["result"]["memory"]["expect"]).split()[0]).quantize(Decimal('0.00'))
                        host_check_dict["result"]["memory"]["expect"] = str(mem) + " GB"

                        if int(float(fact_mem_list[0])) >= int(expect_mem_list[0]):
                            host_check_dict["result"]["memory"]["status"] = True
                        else:
                            host_check_dict["result"]["memory"]["status"] = False

                        # disk
                        expect_disk_list = str(host_check_dict["result"]["disk"]["expect"]).split()
                        fact_disk_list = str(host_check_dict["result"]["disk"]["fact"]).split()

                        logger.info(f"fact disk: {fact_disk_list[0]}, expect disk: {expect_disk_list[0]}")
                        if (float(fact_disk_list[0]) > float(expect_disk_list[0])) and (float(fact_disk_list[0]) == float(expect_disk_list[0])):
                            host_check_dict["result"]["disk"]["status"] = True
                        else:
                            host_check_dict["result"]["disk"]["status"] = False

                        # disk format
                        if host_check_dict["result"]["disk_format"]["expect"] == host_check_dict["result"]["disk_format"]["fact"]:
                            host_check_dict["result"]["disk_format"]["status"] = True
                        else:
                            host_check_dict["result"]["disk_format"]["status"] = False

                        # port set
                        logger.info(f"start check port...")

                        all_port_set = self._get_port_set()
                        able_port_set = set(self._is_open())
                        fact_port = able_port_set - all_port_set
                        fact_port = list(fact_port)

                        logger.info(f" ports ".center(20, "*") )
                        logger.info(f"all_port_set: {all_port_set}, able_port_set:  {able_port_set} fact_port:{fact_port}")
                        if fact_port:
                           host_check_dict["result"]["ports"]["fact"].extend(fact_port)

                        if host_check_dict["result"]["ports"]["fact"]:
                            host_check_dict["result"]["ports"]["status"] = False
                        else:
                            host_check_dict["result"]["ports"]["status"] = True

                        self.ret_list.append(host_check_dict)

            tpl = models.ConfigMap.objects.filter(title="template", key="template").first().value

            # pushes
            all_global_vars_list = ReadExcel(excel_name=request.session.get("excel_name", None)).get_all_global_vars

            push_list = []
            for item in all_global_vars_list:
                if item["key"].endswith("PUSH") and int(item["value"]) == 1:
                    push_list.append(item["key"].split("_")[0])

            if tpl == "local":
                self.ret_list[0]["result"]["pushes"] = push_list
                res = [self.ret_list[0], ]
            else:
                for host in self.ret_list:
                    host["result"].update({"pushes": push_list})
                res = self.ret_list

            return Response({"code": status.HTTP_200_OK, "result": res, "msg": "ok"})
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {e}'})

        finally:

            # listen ports
            self.listen_mutil_port(listen_port_list=distinct_listen_port_list)

    @property
    def max_disk_space(self):
        disk_list = []
        disk = models.DeployModels.objects.filter().all().values("disk")
        for item in disk:
            disk_list.append(Decimal(float(item["disk"].split()[0])).quantize(Decimal('0.00')))

        disk = max(disk_list)
        disk = f"{disk} GB"
        logger.info(f"max disk space is: {disk}")
        return disk

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

            with open(os.path.join(settings.BASE_DIR, "config/ports.json"), 'w', encoding="utf-8") as p:
                 json.dump(listen_port_list, p, ensure_ascii=False)

            cmd = f"python {os.path.join(settings.BASE_DIR, 'utils/listen_ports.py')}"
            logger.info(f"cmd: {cmd}")
            proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
            logger.info(f"Execute listen port scripts Pid: {proc.pid}")

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")

    def handler_port(self,):
        """
        handler port and protocol
        """
        inventory_ini = os.path.join("{BASE_DIR}/hosts.ini".format(BASE_DIR=settings.ANSIBLE["INVENTORY_PATH"]))

        if inventory_ini:
            result = AnsibleAPI(inventory_ini).VariablManager()

            rcx_host_name = result["groups"]["rcx_server"][0]
            result = AnsibleAPI(inventory_ini).VariablManager(hostname=rcx_host_name)

            rcx_port_list = []
            for item in result["rcx_conf"]:
                for k, v in item.items():
                    if str(k) == "NTP_ADDR" or str(k) == "RCX_MGT" or str(k) == "RCDB_NUM":
                        # port_list.append({"port": str(123), "protocol": "udp", "addr": v})
                        continue
                    rcx_port_list.append({"port": int(v), "protocol": "tcp", "addr": "0.0.0.0"})

            # distinct rcx port
            rcx_distinct_port_list = self.distinct(rcx_port_list)

            # rtc ports
            rtc_host_name = result["groups"]["rtc_server"][0]
            result = AnsibleAPI(inventory_ini).VariablManager(hostname=rtc_host_name)

            rtc_port_list = []
            for item in result["rtc_conf"]:
                for k, v in item.items():
                    if str(k).endswith("PORT"):
                        protocol = str(k).split("_")[1]
                        if protocol in ["HTTP", "HTTPS"]:
                            protocol = "tcp"
                        else:
                            protocol = "udp"
                        rtc_port_list.append({"port": int(v), "protocol": protocol, "addr": "0.0.0.0"})
                    elif "CLUSTER" in str(k):
                        v = str(v).split(":")[2]
                        rtc_port_list.append({"port": int(v), "protocol": protocol, "addr": "0.0.0.0"})

            # distinct rtc port
            rtc_distinct_port_list = self.distinct(rtc_port_list)

            rcx_distinct_port_list.extend(rtc_distinct_port_list)
            distinct_listen_port_list = rcx_distinct_port_list
            logger.info(f"Port listen after deduplication: @@@")
            logger.info(f"{json.dumps(distinct_listen_port_list, indent=4, ensure_ascii=False)}")
            return distinct_listen_port_list

    def _get_port_set(self):
        """
        return distinct port list
        """
        port_set = set()
        distinct_listen_port_list = self.handler_port()
        for p in distinct_listen_port_list:
            port_set.add(p["port"])
        return port_set

    def distinct(self, items):
        """
        distinct ports
        """
        questions = map(itemgetter('port'), items)
        df = pd.DataFrame({
            'items': items,
            'port': questions
        })
        return df.drop_duplicates(['port'])['items'].tolist()

    def _is_open(self,):
        """
        check port is open
        """
        port, protocol, addr, able_port_list = [],[],[],[]
        try:

            # listen ports
            distinct_listen_port_list = self.handler_port()
            self.listen_mutil_port(listen_port_list=distinct_listen_port_list)

            for p in distinct_listen_port_list:
                port, protocol, addr = p["port"], p["protocol"], p["addr"]

                if protocol == "udp":
                    logger.info(f"udp protocol: {p}")
                    ADDR = (str(addr), int(port))
                    sk_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sk_udp.settimeout(10)
                    sk_udp.sendto(b"...", ADDR)
                    recv_data = sk_udp.recvfrom(1024)
                    recv_msg = recv_data[0]
                    send_addr = recv_data[1]
                    sk_udp.close()
                    logger.info("{send_addr}: {recv_msg}".format(send_addr=str(send_addr), recv_msg=recv_msg.decode("utf-8")))
                    continue
                else:
                    logger.info(f"tcp protocol: {p}")
                    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sk.settimeout(5)
                    ADDR = (str(addr), int(port))
                    result = sk.connect_ex(ADDR)
                    # sk.shutdown(2)
                    sk.close()

                    if result == 0:
                        logger.info(f"{port} on {addr} is open!")
                        continue

        except socket.timeout as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            logger.info(f"{port} on {addr} is down!")
            able_port_list.append(port)
        finally:
            return able_port_list

    def get_cmdb_info(self):
        """
        use ansible setup module get cmdb info
        """
        try:
            # update cmdb info
            inventory_ini = os.path.join("{BASE_DIR}/hosts.ini".format(BASE_DIR=settings.ANSIBLE["INVENTORY_PATH"], ))

            if inventory_ini:
                cmdb_dict = AnsibleAPI(inventory_ini).cmdb()
                return True, cmdb_dict

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            logger.error(f"ansible setup module excute failed: {e}")
            return False, {}

    @property
    def _get_private_ip(self):
        """
        get host private ip
        """
        try:
            ip_info = []
            info = psutil.net_if_addrs()
            for k, v in info.items():
                for item in v:
                    if item[0] == 2 and not item[1] == '127.0.0.1':
                        ip_info.append((k, item[1]))

            return ip_info[0][1]
        except Exception as e:
            return False

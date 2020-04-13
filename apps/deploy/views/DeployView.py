#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: DeployView.py
@time: 2020/03/14 09:39
@contact: shu_ke163@163.com
@software:  deploy
"""

import os
import sys
import signal
import traceback
import subprocess
from ruamel import yaml
from django.conf import settings
from rest_framework.response import Response
from rest_framework import generics, status
from apps.deploy.serializers import LicenseSerializer
from rest_framework.renderers import JSONRenderer
from apps.core.renders import CustomJSONRenderer
from drf_yasg.utils import swagger_auto_schema
from utils.HandlerVars import ApplicationConfig
from subprocess import check_output
from door.celery import app
from apps.deploy import models
from apps.deploy.conf import ParseSvcSort
from django.db.models import Q
from utils.HandleExcel import ReadExcel
from apps.deploy.tasks.AnsiblePlaybookTask import excute_ansible_playbook_shell

from celery.result import AsyncResult

import logging

logger = logging.getLogger("door")


class GenerateAnsiblePlaybook(object):
    """
    Generate ansible excute playbook file
    """

    def __init__(self, request):
        self._play = None
        self.request = request
        self.tpl = self.get_deploy_model
        self.excel_name = request.session.get("excel_name", None)
        self.ansible_playbook_path = os.path.join(os.path.abspath(os.path.join(settings.ANSIBLE["INVENTORY_PATH"], "../")), f"{self.tpl}.yml")
        self.playbook_list = []

        logger.info(f"ansible playbook path is: {self.ansible_playbook_path}")

    def write_playbook(self):
        """
        write playbook file
        """

        business = models.BusinessLine.objects.filter().values("name")

        for b in business:
            business = str(b["name"]).lower()
            svc_sort_list = ParseSvcSort(business=business).get_svc_sort_list

            for item in svc_sort_list:
                item_dict = {}
                item_dict["hosts"] = item[0]

                # rcdb
                if item[0] == settings.RCDB_DICT["RCDB_GROUP_NAME"]:

                    rcdb_port = settings.RCDB_DICT["START_PORT"]
                    rcdb_port_list = [rcdb_port + num for num in range(0, self.get_rcdb_num())]

                    for role in item[1]["roles"]:
                        item_dict.setdefault("roles", []).append({"role": role, "tags": item[0]})

                    if "vars" in item[1].keys():
                        item_dict.setdefault("vars", {
                            "inst_name": ["{name}.inst-{num}".format(name=item[0], num=num) for num in
                                        range(0, self.get_rcdb_num())]}).update(**item[1]["vars"],
                                                                                **{"rcdb_port": rcdb_port_list})
                    else:
                        item_dict.setdefault("vars", {
                            "inst_name": ["{name}.inst-{num}".format(name=item[0], num=num) for num in
                                        range(0, self.get_rcdb_num())]}).update(
                            {"rcdb_port": rcdb_port_list})

                        self.playbook_list.append(item_dict)

                    continue

                for role in item[1]["roles"]:

                    item_dict.setdefault("roles", []).append({"role": role, "tags": item[0]})
                    if "vars" in item[1].keys():
                        item_dict.setdefault("vars", {}).update(**{"inst_name": f"{item[0]}.inst-0"}, **item[1]["vars"])
                    elif item[0] != "all":
                        item_dict.setdefault("vars", {}).update({"inst_name": f"{item[0]}.inst-0"})

                self.playbook_list.append(item_dict)

            # print(json.dumps(self.playbook_list, indent=4, ensure_ascii=False))

        with open(self.ansible_playbook_path, "w", encoding="utf-8") as f:
            yaml.round_trip_dump(self.playbook_list, f, default_flow_style=False, allow_unicode=True, indent=2)

        return self.playbook_list

    @property
    def get_deploy_model(self):
        tpl = models.ConfigMap.objects.filter(title="template", key="template").first().value
        return tpl

    def get_rcdb_num(self):
        all_global_vars_list = ReadExcel(excel_name=self.excel_name).get_all_global_vars
        for item in all_global_vars_list:
            if item["key"] == settings.RCDB_DICT["RCDB_NUM_KEY"]:
                value = int(item["value"])
                return value


class DeployListView(generics.ListAPIView, GenerateAnsiblePlaybook):
    """
    deploy api view
    """
    queryset = models.ConfigMap.objects.all().order_by('-id')
    serializer_class = LicenseSerializer

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    BASE_DIR = "BASE_DIR"
    playbook_list = []

    def get_queryset(self):
        queryset = self.queryset
        search = self.request.query_params.get("name", None)
        if search is not None:
            queryset = queryset.filter(Q(name__contains=search))
        else:
            queryset = queryset.filter(name="rcx")
        return queryset

    @swagger_auto_schema(operation_description='GET /api/v1/deploy/do_deploy',
                         responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):
        try:
            
            # groups of all.yml 
            ret = self.ansible_group_all_vars(request)

            # kill listen port scripts
            self.kill_listen_port_scripts_pid()

            # Generate playbook file

            svc_sort_list = GenerateAnsiblePlaybook(request).write_playbook()

            logger.info(f"ansible playbook list: {svc_sort_list}")

            revoke, task_id = self.revoke_current_task(request)
            if revoke:
                logger.info(f"revoke task id is: {task_id}")

            # excute ansible playbook
            tpl = self.get_deploy_model
            result = excute_ansible_playbook_shell.delay(yml_name=tpl)

            if "task_id" in request.session.__dict__["_session_cache"].keys():
                del request.session["task_id"]

            request.session["task_id"] = result.id

            logger.info(f"deploy task id: {result.id}")

            res = {"task-id": result.id}
            return Response({"code": status.HTTP_200_OK, "result": res, "msg": "ok"})
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            return Response(
                {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": f'{e.__class__.__name__}: {traceback.print_exc()}'})

    def ansible_group_all_vars(self, request):
        """
        write ansible global all.yml
        """

        business_list = models.BusinessLine.objects.filter().all().values()

        global_conf, rcx_conf, rtc_conf = ApplicationConfig(name="base").read, ApplicationConfig(name="rcx").read, ApplicationConfig(name="rtc").read

        # excel global vars
        excel_name = request.session.get("excel_name", None)
        all_global_vars = ReadExcel(excel_name=excel_name).get_all_global_vars

        ret, business = {}, []
        ret["global"] = global_conf.get("global", None)
        excel_name = request.session.get("excel_name", None)

        vars_dict = {}
        for bus in business_list:
            name ,sort = str(bus["name"]).lower(), bus["sort"]
            business.append({"name": name,"sort": sort})

            business_config_list = []
            for item in all_global_vars[:-1]:
                if item["business"] == name:
                    business_config_list.append(item)

            ret.setdefault(name, {}).update(**{"data": business_config_list})

            for key, val in ret.items():
                for item in val["data"]:
                    vars_dict.setdefault(key, {}).update({item["key"]: item["value"]})

            if self.BASE_DIR in vars_dict[name].keys():
                del vars_dict[name]["BASE_DIR"]

                base_dir = vars_dict[name].pop("BASE_DIR", "/data")
                vars_dict["global"].update({"BASE_DIR": base_dir})

        # global keys
        license = request.session.get("license", None)
        vars_dict.update({"base_path": vars_dict["global"]["BASE_DIR"]})
        vars_dict.update({"python_path": vars_dict["global"]["python_path"]})
        vars_dict.update({"ansible_python_interpreter": vars_dict["global"]["ansible_python_interpreter"]})
        vars_dict.update({"mysql_host": vars_dict["global"]["mysql_host"]})
        vars_dict.update({"license": license})

        # rcdb vars
        rcdb_list = []
        for item in all_global_vars:
            if item["key"] == settings.RCDB_DICT["RCDB_NUM_KEY"]:
                value = int(item["value"])
                for num in range(0, int(value)):
                    rcdb_list.append({"ip": "127.0.0.1", "name": f"{settings.RCDB_DICT['RCDB_GROUP_NAME']}.inst-{num}",
                                    "port": int(settings.RCDB_DICT["START_PORT"] + num)})
        vars_dict.update({"rcdbs": rcdb_list})
        
        logger.debug(f"ansible playbook vars: {vars_dict}")

        with open(os.path.join(settings.ANSIBLE["INVENTORY_PATH"], f"group_vars/all.yml"), "w", encoding="utf-8") as f:
            yaml.round_trip_dump(vars_dict, f, default_flow_style=False, allow_unicode=True, indent=2)

        return ret

    def kill_listen_port_scripts_pid(self,):
        """
        kill listen port scripts
        """
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

    def revoke_current_task(self, request):
        """
        stop current task
        """
        if request.path_info.endswith("retry_deploy"):
            models.DeployModels.objects.all().update(status=0)
            if "task_id" in request.session.__dict__["_session_cache"].keys():
                task_id = request.session.get("task_id", None)
                if task_id:
                    app.control.revoke(task_id, terminate=True)
                    return True, task_id

        return False, None


class CeleryResultListView(generics.ListAPIView):
    """
    celery result view
    """
    queryset = models.ConfigMap.objects.all().order_by('-id')

    renderer_classes = (CustomJSONRenderer, JSONRenderer)

    @swagger_auto_schema(operation_description='GET /api/v1/deploy/status',
                         responses={status.HTTP_200_OK: None})
    def get(self, request, *args, **kwargs):

        try:
            response = {"status": None}

            task_id = request.session.get("task_id", None)
            if task_id:

                logger.info(f"Query task execution results: {task_id}")

                asyncTask = AsyncResult(id=task_id, app=app)

                logger.info(f"task id: {asyncTask.task_id}, task name: {excute_ansible_playbook_shell.name}")

                if asyncTask.successful():
                    result = asyncTask.get()
                    logger.info(
                        f"task name: {excute_ansible_playbook_shell.__name__}, task id: {task_id} status: {asyncTask.state}")

                    response["status"] = self._task_status()
                elif asyncTask.failed():
                    logger.info(
                        f"task name: {excute_ansible_playbook_shell.__name__}, task id: {task_id} status: {asyncTask.status}")
                    response["status"] = -1
                elif asyncTask.status == 'PENDING':
                    logger.info(
                        f"task name: {excute_ansible_playbook_shell.__name__}, task id: {task_id} status: {asyncTask.status}")
                    response["status"] = 1
                elif asyncTask.status == 'RETRY':
                    logger.info(
                        f"task name: {excute_ansible_playbook_shell.__name__}, task id: {task_id} status: {asyncTask.status}")
                    response["status"] = 3
                elif asyncTask.status == 'STARTED':
                    logger.info(
                        f"task name: {excute_ansible_playbook_shell.__name__}, task id: {task_id} status: {asyncTask.status}")
                    response["status"] = 0
            else:
                response["status"] = self._task_status()
            return Response({"code": status.HTTP_200_OK, "result": response, "msg": "ok"})
        except Exception as e:
            return Response({"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "result": response,
                             "msg": f'{e.__class__.__name__}: {e}'})

    def _task_status(self):
        status_list = models.DeployModels.objects.filter().all().values("status")
        if status_list:
            st = set([item["status"] for item in status_list]).pop()
            return st
        return 0

        
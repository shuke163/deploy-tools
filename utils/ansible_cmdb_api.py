#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: ansible_api.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/07 14:48
@software:  door backend
"""

import os
import sys
import datetime
import json
import shutil
import logging
import operator
from decimal import Decimal
from django.conf import settings
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible import context
import ansible.constants as C
from ansible.inventory.host import Host
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase
from distutils.sysconfig import get_python_lib
from functools import partial

PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "door.settings")

import django

django.setup()

from apps.host import models

logger = logging.getLogger("door")


def current_time():
    return '%sZ' % datetime.datetime.utcnow().isoformat()


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'tomysql'

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)
        self.results = []
        self.host_unreachable = {}
        self.host_failed = {}
        self.host_ok = {}

    def _new_play(self, play):
        return {
            'play': {
                'name': play.get_name(),
                'id': str(play._uuid),
                'duration': {
                    'start': current_time()
                }
            },
            'tasks': []
        }

    def _new_task(self, task):
        return {
            'task': {
                'name': task.get_name(),
                'id': str(task._uuid),
                'duration': {
                    'start': current_time()
                }
            },
            'hosts': {}
        }

    def v2_runner_on_ok(self, result, **kwargs):
        hostname = result._host.get_name()
        logger.info(f"ansible v2_runner_on_ok hostname: {hostname}")
        disk_map = {}
        try:
            host = result._result["ansible_facts"]
            host_info = {}
            host_info["hostname"] = hostname
            host_info["fqdn"] = host.get("ansible_fqdn", None)
            host_info["cpu"] = str(host.get("ansible_processor_vcpus", None)) + "c"
            memory = Decimal(round(host.get("ansible_memtotal_mb") / 1024) + 1).quantize(Decimal('0.00'))
            host_info["memory"] = "{memory} {unit}".format(memory=str(memory), unit="GB")
            
            for k, v in host["ansible_devices"].items():
                disk_map[k] = float(v["size"].split()[0])

            disk_symbol = max(disk_map, key=disk_map.get)
            disk = str(disk_map[disk_symbol]) + " GB"
            host_info["disk"] = disk
            mount_map = []
            for mount in host["ansible_mounts"]:
                mnt = {}
                mnt["device"] = mount["device"]
                mnt["fstype"] = mount["fstype"]
                mnt["mount"] = mount["mount"]
                mnt["size_total"] = mount["size_total"]
                mount_map.append(mnt)

            mount_index = {}
            for i in mount_map:
                for key, value in i.items():
                    mount_index[mount_map.index(i)] = value
            sorted_x = sorted(mount_index.items(), key=operator.itemgetter(1))

            li2 = []
            for j in sorted_x:
                li2.append(j[0])

            mount_info = []
            for k in li2:
                mount_info.append(mount_map[k])

            host_info["mount_point"] = mount_info[-1]["mount"]
            host_info["disk_format"] = mount_info[-1]["fstype"]
            host_info["ipv4"] = host.get("ansible_default_ipv4")["address"]
            host_info["arch"] = host.get("ansible_architecture", None)
            host_info["os_type"] = host.get("ansible_distribution", None)
            host_info["os_version"] = host.get("ansible_distribution_version", None)
            host_info["machine_id"] = host.get("ansible_machine_id", None)
            host_info["macaddress"] = host.get("ansible_default_ipv4")["macaddress"]
            host_info["kernel_info"] = host.get("ansible_kernel", None)
            host_info["virtualization_type"] = host.get("ansible_virtualization_type", None)

            import json
            print(json.dumps(host_info, indent=4, ensure_ascii=False))

            self.results.append(host_info)
            self.host_ok[result._host.get_name()] = result

            models.Cmdb.objects.update_or_create(hostname=host_info["hostname"], defaults=host_info)

        except Exception as e:
            logger.error(f"get ansible facts result faild: {e.__class__.__name__}: {e}")
            raise Exception("{hostname} already exist".format(hostname=hostname))

    def v2_runner_on_unreachable(self, result):
        logger.info("unreachable host: {}".format(result._host.get_name()))
        self.results.append({result._host.get_name(): result._result})
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        # print(result.__dict__)
        logger.info("host failed: {}".format(result._host.get_name()))
        self.results.append({result._host.get_name(): result._result})
        self.host_failed[result._host.get_name()] = result

    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))

    def v2_playbook_on_handler_task_start(self, task):
        self.results[-1]['tasks'].append(self._new_task(task))

    def _convert_host_to_name(self, key):
        if isinstance(key, (Host,)):
            return key.get_name()
        return key

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        hosts = sorted(stats.processed.keys())

        summary = {}
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s

        custom_stats = {}
        global_custom_stats = {}

        if self.get_option('show_custom_stats') and stats.custom:
            custom_stats.update(dict((self._convert_host_to_name(k), v) for k, v in stats.custom.items()))
            global_custom_stats.update(custom_stats.pop('_run', {}))

        output = {
            'plays': self.results,
            'stats': summary,
            'custom_stats': custom_stats,
            'global_custom_stats': global_custom_stats,
        }

        self._display.display(json.dumps(output, cls=AnsibleJSONEncoder, indent=4, sort_keys=True))

    def _record_task_result(self, on_info, result, **kwargs):
        """This function is used as a partial to add failed/skipped info in a single method"""
        host = result._host
        task = result._task
        task_result = result._result.copy()
        task_result.update(on_info)
        task_result['action'] = task.action
        self.results[-1]['tasks'][-1]['hosts'][host.name] = task_result
        end_time = current_time()
        self.results[-1]['tasks'][-1]['task']['duration']['end'] = end_time
        self.results[-1]['play']['duration']['end'] = end_time

        return self.results

    # def __getattribute__(self, name):
    #     """Return ``_record_task_result`` partial with a dict containing skipped/failed if necessary"""
    #     if name not in ('v2_runner_on_ok', 'v2_runner_on_failed', 'v2_runner_on_unreachable', 'v2_runner_on_skipped'):
    #         return object.__getattribute__(self, name)
    #
    #     on = name.rsplit('_', 1)[1]
    #
    #     on_info = {}
    #     if on in ('failed', 'skipped'):
    #         on_info[on] = True
    #
    #     # logger.info("Event: {name}, Task status: {status}".format(name=name, status=on))
    #     return partial(self._record_task_result, on_info)


class AnsibleAPI(object):
    """
    执行ansible模块或者playbook的类
    """

    def __init__(self, inventory_path):
        self.inventory_path = inventory_path
        self.loader = DataLoader()
        self.callback = None

    def cmdb(self):
        module_path = os.path.join(get_python_lib(), "ansible")
        context.CLIARGS = ImmutableDict(connection='smart',
                                        module_path=[module_path, ],
                                        forks=50, become=None,
                                        become_method=None, become_user=None, check=False, diff=False)

        passwords = dict(vault_pass='secret')

        self.callback = CallbackModule()

        inventory = InventoryManager(loader=self.loader, sources=self.inventory_path)

        print(inventory.list_groups(), inventory.get_groups_dict(), inventory.add_group("cmdb"))
        # print(inventory.list_groups(), inventory.list_hosts())

        variable_manager = VariableManager(loader=self.loader, inventory=inventory)

        play_source = dict(
            name="Ansible CMDB",
            hosts=str(inventory.groups["all"]),
            gather_facts='no',
            tasks=[
                # dict(action=dict(module='shell', args='ls'), register='shell_out'),
                # dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
                # dict(action=dict(module='shell', args='whoami')),
                dict(action=dict(module='setup', )),
            ]
        )

        # Create play object, playbook objects use .load instead of init or new methods,
        play = Play().load(play_source, variable_manager=variable_manager, loader=self.loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=self.loader,
                passwords=passwords,
                stdout_callback=self.callback,
                # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
            )
            tqm._stdout_callback = self.callback
            tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods

            result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
            for host, result in self.callback.host_ok.items():
                result_raw['success'][host] = result._result["ansible_facts"]
            for host, result in self.callback.host_failed.items():
                result_raw['failed'][host] = result._result
            for host, result in self.callback.host_unreachable.items():
                result_raw['failed'][host] = result._result

    #        print(json.dumps(result_raw, indent=4))

            return result_raw

        finally:
            if tqm is not None:
                tqm.cleanup()

            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def runplaybook(self):
        module_path = os.path.join(get_python_lib(), "ansible")
        context.CLIARGS = ImmutableDict(connection='smart',
                                        module_path=[module_path, ],
                                        forks=50, become=None,
                                        become_method=None, become_user=None, check=False, diff=False)

        passwords = dict(vault_pass='secret')

        self.callback = CallbackModule()

        inventory = InventoryManager(loader=self.loader, sources=self.inventory_path)

        print(inventory.list_groups(), inventory.get_groups_dict(), inventory.add_group("cmdb"))
        # print(inventory.list_groups(), inventory.list_hosts())

        variable_manager = VariableManager(loader=self.loader, inventory=inventory)

        play_source = dict(
            name="Ansible CMDB",
            hosts=str(inventory.groups["all"]),
            gather_facts='no',
            tasks=[
                # dict(action=dict(module='shell', args='ls'), register='shell_out'),
                # dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
                # dict(action=dict(module='shell', args='whoami')),
                dict(action=dict(module='setup', )),
            ]
        )

        # Create play object, playbook objects use .load instead of init or new methods,
        play = Play().load(play_source, variable_manager=variable_manager, loader=self.loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=self.loader,
                passwords=passwords,
                stdout_callback=self.callback,
                # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
            )
            tqm._stdout_callback = self.callback
            tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods

            result_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
            for host, result in self.callback.host_ok.items():
                result_raw['success'][host] = result._result["ansible_facts"]
            for host, result in self.callback.host_failed.items():
                result_raw['failed'][host] = result._result
            for host, result in self.callback.host_unreachable.items():
                result_raw['failed'][host] = result._result

            print(json.dumps(result_raw, indent=4))

            return result_raw

        finally:
            if tqm is not None:
                tqm.cleanup()

            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def VariablManager(self, hostname=None):
        inventory = InventoryManager(loader=self.loader,
                                     sources=os.path.join(settings.BASE_DIR, "apps/playbook/inventory/hosts.ini"))
        vm = VariableManager(loader=self.loader, inventory=inventory)

        host = inventory.get_host(hostname)

        vm.set_host_variable(host=host, varname="company", value="RongCloud")

        # 获取指定主机的变量
        # print(vm.get_vars(host=host))

        return vm.get_vars(host=host)


if __name__ == '__main__':
    inventory_path = os.path.join(PATH, 'apps/playbook/inventory/hosts.ini')
    AnsibleAPI(inventory_path).cmdb()

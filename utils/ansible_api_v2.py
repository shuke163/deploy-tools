#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: ansible_api_v2.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/10 09:46
@software:  Door
"""
import os
import sys
import re
import json
import logging
import datetime
import shutil
from ansible import constants as C
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.inventory.host import Host
from ansible.parsing.ajson import AnsibleJSONEncoder
from django.conf import settings

PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, PATH)
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Door.settings")
#
# import django
#
# django.setup()

# from apps.host.models import Cmdb

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

        try:
            host = result._result["ansible_facts"]

            host_info = {}
            host_info["hostname"] = hostname
            host_info["fqdn"] = host.get("ansible_fqdn", None)
            host_info["cpu"] = str(host.get("ansible_processor_vcpus", None)) + "c"
            host_info["memory"] = str(round(host.get("ansible_memtotal_mb") / 1024) + 1) + " GB"
            host_info["disk"] = host.get("ansible_devices")["vda"]["size"]
            host_info["disk_format"] = host.get("ansible_mounts")[0]["fstype"]
            host_info["mount_point"] = host.get("ansible_mounts")[0]["mount"]
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

            # models.Cmdb.objects.get_or_create(host_info)

        except Exception as e:
            logger.error(f"get ansible facts result faild: {e.__class__.__name__}: {e}")
            raise Exception("{hostname} already exist".format(hostname=hostname))

    def v2_runner_on_unreachable(self, result):
        logger.info("unreachable host: %s" % result._host.get_name())
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        # print(result.__dict__)
        logger.info("主机执行失败: ".format(result._host.get_name()))
        self.results.append({result._host.get_name(): result})

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


class DeployResultsCollector(CallbackBase):
    """
    直接执行模块命令的回调类
    """

    def __init__(self, sock, send_msg, *args, **kwargs):
        super(DeployResultsCollector, self).__init__(*args, **kwargs)
        self.sock = sock
        self.send_msg = send_msg

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '主机{host}不可达！==> {stdout}\n剔除该主机!\n'.format(host=result._host.name, stdout=result._result.get('msg'))
        else:
            data = '主机{host}不可达！==> {stdout}\n剔除该主机!\n'.format(host=result._host.name,
                                                               stdout=json.dumps(result._result, indent=4))

        self.chk_host_list(data, result._host.name)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        data = '主机{host}执行任务成功！\n'.format(host=result._host.name)
        self.sock.send_save(data, send=self.send_msg)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'stderr' in result._result:
            data = '<p style="color: #FF0000">\n主机{host}执行任务失败 ==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=result._result.get('stderr').encode().decode('utf-8'))
        elif 'msg' in result._result:
            data = '<p style="color: #FF0000">\n主机{host}执行任务失败 ==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=result._result.get('msg'))
        else:
            data = '<p style="color: #FF0000">\n主机{host}执行任务失败 ==> {stdout}\n剔除该主机！</p>'.format(
                host=result._host.name, stdout=json.dumps(result._result, indent=4))
        self.chk_host_list(data, result._host.name)

    def chk_host_list(self, data, host):
        self.sock.send_save(data, send=self.send_msg)
        self.sock.host_list.remove(host)
        self.sock.host_fail.append(host)
        if len(self.sock.host_list) == 0:
            self.sock.send('<p style="color: #FF0000">所有主机均部署失败！退出部署流程！</p>', close=True)
            self.sock.deploy_results.append('<p style="color: #FF0000">所有主机均部署失败！退出部署流程！</p>')


class ModuleResultsCollector(CallbackBase):
    """
    直接执行模块命令的回调类
    """

    def __init__(self, sock=None, *args, **kwargs):
        super(ModuleResultsCollector, self).__init__(*args, **kwargs)
        self.module_results = []
        self.sock = sock

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '<code style="color: #FF0000">\n{host} | unreachable | rc={rc} >> \n{stdout}\n</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                stdout=result._result.get('msg').encode().decode('utf-8'))
        else:
            data = '<code style="color: #FF0000">\n{host} | unreachable >> \n{stdout}\n</code>'.format(
                host=result._host.name,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        if self.sock:
            self.sock.send(data)
        self.module_results.append(data)

    def v2_runner_on_ok(self, result, *args, **kwargs):

        if 'rc' in result._result and 'stdout' in result._result:
            data = '<code style="color: #008000">\n{host} | success | rc={rc} >> \n{stdout}\n</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                stdout=result._result.get('stdout').encode().decode('utf-8'))
        elif 'results' in result._result and 'rc' in result._result:
            data = '<code style="color: #008000">\n{host} | success | rc={rc} >> \n{stdout}\n</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                stdout=result._result.get('results')[0].encode().decode('utf-8'))
        elif 'module_stdout' in result._result and 'rc' in result._result:
            data = '<code style="color: #008000">\n{host} | success | rc={rc} >> \n{stdout}\n</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                stdout=result._result.get('module_stdout').encode().decode('utf-8'))
        else:
            data = '<code style="color: #008000">\n{host} | success >> \n{stdout}\n</code>'.format(
                host=result._host.name,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        if self.sock:
            self.sock.send(data)
        self.module_results.append(data)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'stderr' in result._result:
            data = '<code style="color: #FF0000">\n{host} | failed | rc={rc} >> \n{stdout}\n</code>'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                stdout=result._result.get('stderr').encode().decode('utf-8'))
        elif 'module_stdout' in result._result:
            data = '<code style="color: #FF0000">\n{host} | failed | rc={rc} >> \n{stdout}\n</code>'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                stdout=result._result.get('module_stdout').encode().decode('utf-8'))
        else:
            data = '<code style="color: #FF0000">\n{host} | failed >> \n{stdout}\n</code>'.format(
                host=result._host.name,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        if self.sock:
            self.sock.send(data)
        self.module_results.append(data)


class PlayBookResultsCollector(CallbackBase):
    """
    执行playbook的回调类
    """

    def __init__(self, sock, *args, **kwargs):
        super(PlayBookResultsCollector, self).__init__(*args, **kwargs)
        self.playbook_results = []
        self.sock = sock

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            msg = format('<code style="color: #FFFFFF">\nPLAY', '*<150') + ' \n</code>'
        else:
            msg = format(f'<code style="color: #FFFFFF">\nPLAY [{name}]', '*<150') + ' \n</code>'
        self.send_save(msg)

    def v2_playbook_on_task_start(self, task, is_conditional):
        msg = format(f'<code style="color: #FFFFFF">\nTASK [{task.get_name()}]', '*<150') + ' \n</code>'
        self.send_save(msg)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if result.is_changed():
            data = '<code style="color: #FFFF00">[{}]=> changed\n</code>'.format(result._host.name)
        else:
            data = '<code style="color: #008000">[{}]=> ok\n</code>'.format(result._host.name)
        self.send_save(data)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'changed' in result._result:
            del result._result['changed']
        data = '<code style="color: #FF0000">[{}]=> {}: {}\n</code>'.format(result._host.name, 'failed',
                                                                            self._dump_results(result._result))
        self.send_save(data)

    def v2_runner_on_unreachable(self, result):
        if 'changed' in result._result:
            del result._result['changed']
        data = '<code style="color: #FF0000">[{}]=> {}: {}\n</code>'.format(result._host.name, 'unreachable',
                                                                            self._dump_results(result._result))
        self.send_save(data)

    def v2_runner_on_skipped(self, result):
        if 'changed' in result._result:
            del result._result['changed']
        data = '<code style="color: #FFFF00">[{}]=> {}: {}\n</code>'.format(result._host.name, 'skipped',
                                                                            self._dump_results(result._result))
        self.send_save(data)

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        data = format('<code style="color: #FFFFFF">\nPLAY RECAP ', '*<150') + '\n'
        self.send_save(data)
        for h in hosts:
            s = stats.summarize(h)
            msg = '<code style="color: #FFFFFF">{} : ok={} changed={} unreachable={} failed={} skipped={}\n</code>'.format(
                h, s['ok'], s['changed'], s['unreachable'], s['failures'], s['skipped'])
            self.send_save(msg)

    def send_save(self, data):
        self.sock.send(data)
        self.playbook_results.append(data)


class MyInventory(InventoryManager):
    """
    用于动态生成Inventory的类.
    """

    def __init__(self, loader, resource=None, sources=None):
        """
        resource的数据格式是一个列表字典，比如
            {
                "group1": {
                    "hosts": [{"ip": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...],
                    "group_vars": {"var1": value1, "var2": value2, ...}
                }
            }
             如果你只传入1个列表，这默认该列表内的所有主机属于default 组,比如
            [{"ip": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...]
        sources是原生的方法，参数是配置的inventory文件路径，可以指定一个，也可以以列表的形式可以指定多个
        """
        super(MyInventory, self).__init__(loader=loader, sources=sources)
        self.resource = resource
        self.dynamic_inventory()

    def add_dynamic_group(self, hosts, group_name, group_vars=None):
        """
        将从数据库读取的组信息，主机信息等生成的resource信息解析成ansible可以读取的内容
        :param hosts: 包含主机所有信息的的列表
        :type hosts: list
        :param group_name:
        :param group_vars:
        :type group_vars: dict
        :return:
        """
        # 添加主机组
        self.add_group(group_name)

        # 添加主机组变量
        if group_vars:
            for key, value in group_vars.items():
                self.groups[group_name].set_variable(key, value)

        for host in hosts:
            ip = host.get('ip')
            port = host.get('port')

            # 添加主机到主机组
            self.add_host(ip, group_name, port)

            username = host.get('username')
            password = host.get('password')

            # 生成ansible主机变量
            self.get_host(ip).set_variable('ansible_ssh_host', ip)
            self.get_host(ip).set_variable('ansible_ssh_port', port)
            self.get_host(ip).set_variable('ansible_ssh_user', username)
            self.get_host(ip).set_variable('ansible_ssh_pass', password)
            self.get_host(ip).set_variable('ansible_sudo_pass', password)

            # 如果使用同一个密钥管理所有机器，只需把下方的注释去掉，ssh_key指定密钥文件，若是不同主机使用不同密钥管理，则需要单独设置主机变量或组变量
            # self.get_host(ip).set_variable('ansible_ssh_private_key_file', ssh_key)

            # set other variables
            for key, value in host.items():
                if key not in ["ip", "port", "username", "password"]:
                    self.get_host(ip).set_variable(key, value)

    def dynamic_inventory(self):
        if isinstance(self.resource, list):
            self.add_dynamic_group(self.resource, 'default')
        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.items():
                self.add_dynamic_group(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("group_vars"))


class ANSRunner(object):
    """
    执行ansible模块或者playbook的类，这里默认采用了用户名+密码+sudo的方式
    """

    def __init__(self, resource=None, sources=None, sock=None, **kwargs):
        Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'timeout', 'remote_user',
                                         'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                         'sftp_extra_args', 'strategy',
                                         'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass',
                                         'verbosity', 'retry_files_enabled',
                                         'check', 'listhosts', 'listtasks', 'listtags', 'syntax', 'diff',
                                         'gathering', 'roles_path'])
        self.options = Options(connection='smart',
                               module_path=None,
                               forks=50, timeout=10,
                               remote_user=kwargs.get('remote_user', None), ask_pass=False, private_key_file=None,
                               ssh_common_args=None,
                               ssh_extra_args=None,
                               sftp_extra_args=None, strategy='free', scp_extra_args=None,
                               become=kwargs.get('become', None),
                               become_method=kwargs.get('become_method', None),
                               become_user=kwargs.get('become_user', None), ask_value_pass=False, verbosity=None,
                               retry_files_enabled=False, check=False, listhosts=False,
                               listtasks=False, listtags=False, syntax=False, diff=True, gathering='smart',
                               roles_path=os.path.join(PATH, "../roles"))
        self.loader = DataLoader()
        self.inventory = MyInventory(resource=resource, loader=self.loader, sources=sources)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.passwords = dict(sshpass=None, becomepass=None)
        self.callback = None
        self.sock = sock

    def run_module(self, host_list, module_name, module_args=None, deploy=False, send_msg=True):
        """
        run module from ansible ad-hoc.
        """
        self.callback = CallbackModule()

        if module_args:
            play_source = dict(
                name="Ansible play",
                hosts=host_list,
                gather_facts='no',
                tasks=[dict(action=dict(module=module_name, args=module_args))]
            )
        else:
            play_source = dict(
                name="Ansible play",
                hosts=host_list,
                gather_facts='no',
                tasks=[dict(action=dict(module=module_name, ))]
            )

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        # actually run it
        tqm = None

        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                # options=self.options,
                passwords=self.passwords,
                stdout_callback=self.callback,
            )

            C.HOST_KEY_CHECKING = False  # 关闭第一次使用ansible连接客户端时输入命令
            tqm.run(play)
        except Exception as e:
            logger.error('执行 {} 失败，原因: {}'.format(module_name, e))
        finally:
            if tqm is not None:
                tqm.cleanup()
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def run_playbook(self, playbook_path, extra_vars=None):
        """
        run ansible playbook
        """
        try:
            self.callback = PlayBookResultsCollector(sock=self.sock)
            if extra_vars:
                self.variable_manager.extra_vars = extra_vars
            executor = PlaybookExecutor(
                playbooks=[playbook_path], inventory=self.inventory, variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
            )
            executor._tqm._stdout_callback = self.callback
            C.HOST_KEY_CHECKING = False  # 关闭第一次使用ansible连接客户端时输入命令
            executor.run()
        except Exception as e:
            logger.error('执行{}失败，原因: {}'.format(playbook_path, e))

    @property
    def get_module_results(self):
        return self.callback.results

    @property
    def get_playbook_results(self):
        return self.callback.playbook_results

    @staticmethod
    def handle_setup_data(data):
        """处理setup模块数据，用于收集服务器信息功能"""
        server_facts = {}
        result = json.loads(data[data.index('{'): data.rindex('}') + 1])
        facts = result['ansible_facts']
        server_facts['hostname'] = facts['ansible_hostname']
        server_facts['cpu_model'] = facts['ansible_processor'][-1]
        server_facts['cpu_number'] = int(facts['ansible_processor_count'])
        server_facts['vcpu_number'] = int(facts['ansible_processor_vcpus'])
        server_facts['disk_total'], disk_size = 0, 0
        for k, v in facts['ansible_devices'].items():
            if k[0:2] in ['sd', 'hd', 'ss', 'vd']:
                if 'G' in v['size']:
                    disk_size = float(v['size'][0: v['size'].rindex('G') - 1])
                elif 'T' in v['size']:
                    disk_size = float(v['size'][0: v['size'].rindex('T') - 1]) * 1024
                server_facts['disk_total'] += round(disk_size, 2)
        server_facts['ram_total'] = round(int(facts['ansible_memtotal_mb']) / 1024)
        server_facts['kernel'] = facts['ansible_kernel']
        server_facts['system'] = '{} {} {}'.format(facts['ansible_distribution'],
                                                   facts['ansible_distribution_version'],
                                                   facts['ansible_userspace_bits'])
        server_model = facts['ansible_product_name']

        # 获取网卡信息
        nks = []
        for nk in facts.keys():
            networkcard_facts = {}
            if re.match(r"^ansible_(eth|bind|eno|ens|em)\d+?", nk):
                networkcard_facts['network_card_name'] = facts.get(nk).get('device')
                networkcard_facts['network_card_mac'] = facts.get(nk).get('macaddress')
                networkcard_facts['network_card_ip'] = facts.get(nk).get('ipv4').get('address') if 'ipv4' in facts.get(
                    nk) else 'unknown'
                networkcard_facts['network_card_model'] = facts.get(nk).get('type')
                networkcard_facts['network_card_mtu'] = facts.get(nk).get('mtu')
                networkcard_facts['network_card_status'] = 1 if facts.get(nk).get('active') else 0
                nks.append(networkcard_facts)
        return server_facts, server_model, nks

    @staticmethod
    def handle_mem_data(data):
        """
        处理获取的内存信息
        :param data: 通过ansible获取的内存信息
        :return:
        """
        result = json.loads(data[data.index('{'): data.rindex('}') + 1])
        facts = result['ansible_facts']
        return facts['mem_info']


if __name__ == '__main__':
    inventory_path = '/Users/shuke/Work/SCM/Door/apps/playbook/inventory/rcx/hosts.ini'
    ANSRunner(sources=inventory_path).run_playbook(playbook_path=['/Users/shuke/Work/SCM/Door/apps/playbook/test.yml'])

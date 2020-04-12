#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: ansible_playbook_api.py 
@time: 2020/03/18 09:55
@contact: shu_ke163@163.com
@software:  Door
"""

import os
import sys
import json
import logging
import datetime
from optparse import Values
from collections import namedtuple
from ansible import constants as C
from ansible import constants
from ansible import context
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback.default import CallbackModule
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display

    display = Display()

logger = logging.getLogger("door")


def current_time():
    return '%sZ' % datetime.datetime.utcnow().isoformat()


class PlaybookCallback(CallbackModule):
    """重写console输出日志"""

    def __init__(self):
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

    # 重写2.0版本正确stdout
    def v2_runner_on_ok(self, result):

        # print(" ok ".center(30, "="), "\n", json.dumps(result._result, indent=4, ensure_ascii=False))

        # print("==== 2 ====", result.__dict__)

        if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        self._clean_results(result._result, result._task.action)
        delegated_vars = result._result.get('_ansible_delegated_vars', None)

        delegated_vars = self._dump_results(result._result)
        delegated_vars = result._result
        n_delegated_vars = self._dump_results(result)
        # print(n_delegated_vars)

        # self._clean_results(result._result, result._task.action)

        if result._task.action in ('include', 'include_role'):
            return
        elif result._result.get('changed', False):
            if delegated_vars:
                # 自定义输出
                zdy_msg = self.zdy_stdout(json.loads(delegated_vars))
                if zdy_msg:
                    msg = "changed: [%s]%s" % (result._host.get_name(), zdy_msg)
                else:
                    msg = "changed: [%s -> %s]" % (result._host.get_name(), delegated_vars)
            else:
                msg = "changed: [%s]" % result._host.get_name()
            color = C.COLOR_CHANGED

        # 判断是否是第一步 setup

        elif result._result.get('ansible_facts', False):
            msg = "ok: [ %s | %s ]" % (str(result._host), str(result._host.get_groups()))
            color = C.COLOR_OK
        else:
            if delegated_vars:
                # 自定义输出
                zdy_msg = self.zdy_stdout(json.loads(delegated_vars))
                if zdy_msg:
                    msg = "ok: [%s]%s" % (result._host.get_name(), zdy_msg)
                else:
                    msg = "ok: [%s -> %s]" % (result._host.get_name(), delegated_vars)
            else:
                msg = "ok: [%s]" % result._host.get_name()
            color = C.COLOR_OK

        if result._task.loop and 'results' in result._result:
            self._process_items(result)
        else:
            self._display.display(msg, color=color)

        self._handle_warnings(result._result)

    # 自定义输出,格式清晰一些
    def zdy_stdout(self, result):
        msg = ''
        if result.get('delta', False):
            msg += u'\t执行时间:%s' % result['delta']
        if result.get('cmd', False):
            msg += u'\n执行命令:%s' % result['cmd']
        if result.get('stderr', False):
            msg += u'\n错误输出:\n%s' % result['stderr']
        if result.get('stdout', False):
            msg += u'\n正确输出:\n%s' % result['stdout']
        if result.get('warnings', False):
            msg += u'\n警告:%s' % result['warnings']
        return msg

    def display_skipped_hosts(self, result):
        # print(result._result)
        pass

    # def v2_runner_on_ok(self, result, **kwargs):
    #
    #     hostname = result._host.get_name()
    #     logger.info(f"ansible v2_runner_on_ok hostname: {hostname}")
    #     try:
    #
    #         self.host_ok[result._host.get_name()] = result
    #
    #     except Exception as e:
    #         logger.error(f"get ansible facts result faild: {e.__class__.__name__}: {e}")
    #         raise Exception("{hostname} already exist".format(hostname=hostname))

    def v2_runner_on_unreachable(self, result):
        print("=" * 30, result._result)
        logger.info("unreachable host: {}".format(result._host.get_name()))
        self.results.append({result._host.get_name(): result._result})
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        print(" failed ".center(30, '*'), json.dumps(result._result, indent=4, ensure_ascii=False))
        logger.info("host failed: {}".format(result._host.get_name()))
        self.results.append({result._host.get_name(): result._result})
        self.host_failed[result._host.get_name()] = result

    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))

    def v2_playbook_on_handler_task_start(self, task):
        self.results[-1]['tasks'].append(self._new_task(task))

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


class PlayBookJob:
    """
    封装一个playbook接口,提供给外部使用
    """

    def __init__(self, playbooks, inventory, ssh_user='bbs', passwords='null', project_name='all', ack_pass=False,
                 forks=5, ext_vars=None):
        self.playbooks = playbooks
        self.inventory = inventory
        self.ssh_user = ssh_user
        self.passwords = dict(vault_pass=passwords)
        self.project_name = project_name
        self.ack_pass = ack_pass
        self.forks = forks
        self.connection = 'smart'
        self.ext_vars = ext_vars

        ## 用来加载解析yaml文件或JSON内容,并且支持vault的解密
        self.loader = DataLoader()

        # 根据inventory加载对应变量
        self.inventory = InventoryManager(loader=self.loader,
                                          sources='/Users/shuke/Work/SCM/Door/apps/playbook/inventory/rcx/hosts.ini')

        # 管理变量的类，包括主机，组，扩展等变量，之前版本是在 inventory中的
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

        self.variable_manager.set_inventory(self.inventory)

        # # 初始化需要的对象1
        # self.Options = namedtuple('Options',
        #                           ['connection',
        #                            'remote_user',
        #                            'ask_sudo_pass',
        #                            'verbosity',
        #                            'ack_pass',
        #                            'module_path',
        #                            'forks',
        #                            'become',
        #                            'become_method',
        #                            'become_user',
        #                            'check',
        #                            'listhosts',
        #                            'listtasks',
        #                            'listtags',
        #                            'syntax',
        #                            'sudo_user',
        #                            'sudo',
        #                            ])
        #
        # # 初始化需要的对象2
        # self.options = self.Options(connection=self.connection,
        #                             remote_user=self.ssh_user,
        #                             ack_pass=self.ack_pass,
        #                             sudo_user=self.ssh_user,
        #                             forks=self.forks,
        #                             sudo='yes',
        #                             ask_sudo_pass=False,
        #                             verbosity=5,
        #                             module_path=None,
        #                             become=True,
        #                             become_method='sudo',
        #                             become_user='root',
        #                             check=None,
        #                             listhosts=None,
        #                             listtasks=None,
        #                             listtags=None,
        #                             syntax=None,
        #                             )
        self.options = {'verbosity': 0, 'ask_pass': False, 'private_key_file': None, 'remote_user': None,
                        'connection': 'smart', 'timeout': 10, 'ssh_common_args': '', 'sftp_extra_args': '',
                        'scp_extra_args': '', 'ssh_extra_args': '', 'force_handlers': False, 'flush_cache': None,
                        'become': False, 'become_method': 'sudo', 'become_user': 'root', 'become_ask_pass': False,
                        'tags': ['all'], 'skip_tags': [], 'check': False, 'syntax': None, 'diff': False,
                        'inventory': self.inventory, 'listhosts': None, 'subset': None, 'extra_vars': [],
                        'ask_vault_pass': False,
                        'vault_password_files': [], 'vault_ids': [], 'forks': 5, 'module_path': None, 'listtasks': None,
                        'listtags': None, 'step': None, 'start_at_task': None, 'args': ['fake'],
                        '_last_task_banner': None, 'show_per_host_start': None}

        self.ops = Values(self.options)

        # 初始化console输出
        self.callback = PlaybookCallback()

        # 直接开始
        self.run_playbook()

    def run_playbook(self):
        """
        run ansible palybook
        """
        try:
            self.callback = PlaybookCallback()

            context._init_global_context(Values(self.options))

            executor = PlaybookExecutor(
                playbooks=self.playbooks,
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
            )

            # print(executor)

            executor._tqm._stdout_callback = self.callback
            constants.HOST_KEY_CHECKING = False
            constants.DEPRECATION_WARNINGS = False
            constants.RETRY_FILES_ENABLED = False

            result = executor.run()

            print(result)

        except Exception as err:
            logger.error(msg="run playbook failed: {err}".format(err=str(err)))
            return False


if __name__ == '__main__':
    PlayBookJob(playbooks=['/Users/shuke/Work/SCM/Door/apps/playbook/rcx-cluster.yml'],
                inventory='/Users/shuke/Work/SCM/Door/apps/playbook/inventory/rcx/hosts.ini',
                ssh_user='root',
                project_name="test",
                forks=20,
                ext_vars=None
                )

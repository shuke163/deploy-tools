#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: api.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/11 16:36
@software:  Door
"""

import sys
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager


def VariablManagerCode():
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources='/Users/shuke/Work/SCM/Door/apps/playbook/inventory/rcx/hosts.ini')
    vm = VariableManager(loader=loader, inventory=inventory)

    # 必须要先获取主机，然后查询特定主机才能看到某个主机的变量
    host = inventory.get_host("rcx_server_node01")

    # 动态添加变量
    vm.set_host_variable(host=host, varname="AAA", value="aaa")
    # 获取指定主机的变量
    print(vm.get_vars(host=host))


def main():
    VariablManagerCode()


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit()

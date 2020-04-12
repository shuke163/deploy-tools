#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import time
import json
import yaml
import subprocess
from app import app
from app import schema, db


# PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.insert(0, PATH)


def get_playbook_file(product):
    """
    初始化ansible目录结构
    :param product:
    :return:
    """
    inventory_path = os.path.join(app.config["BASE_DIR"], f'app/playbook/inventory/{product}')

    if not os.path.exists(inventory_path):
        os.makedirs(inventory_path)
    group_path = os.path.join(inventory_path, 'group_vars')
    if not os.path.exists(group_path):
        os.makedirs(group_path)
    group = os.path.join(group_path, 'all.yaml')

    inventory = os.path.join(inventory_path, 'hosts.ini')
    playbook_file = os.path.join(app.config["BASE_DIR"], f'app/playbook/{product}-cluster.yaml')

    return group, inventory, playbook_file


def set_deploy_status(product, status):
    """
    更新执行步骤的状态
    :param product:
    :param status:
    :return:
    """
    app.logger.info(f"{product} deploy status is: {status}")
    deploy = schema.get_deploy(product)
    deploy.status = status
    db.session.commit()


def create_playbook(product):
    """
    序列化ansible运行时依赖的文件
    :param product:
    :return:
    """
    deploy = schema.get_deploy(product)
    if not deploy or deploy.status != 'init':
        return
    with open(deploy.deploy_file, 'rb') as f:
        data = json.loads(f.read().decode('utf-8'))

    group, inventory, playbook_file = get_playbook_file(product)
    with open(group, 'w') as fw:
        fw.write(yaml.safe_dump(data['vars'].get('all', dict())))

    with open(inventory, 'w') as fw:
        for line in data['hostini']:
            fw.write(line + '\n')

    with open(playbook_file, 'w') as fw:
        fw.write(yaml.safe_dump(data['playbooks']))

    set_deploy_status(product, 'start')


def _execute(product):
    """
    执行playbook
    :param product:
    :return:
    """
    _, inventory, playbook_file = get_playbook_file(product)
    playbook_path = os.path.join(app.config["BASE_DIR"], 'app/playbook')
    cmd = f"cd {playbook_path} && /opt/python3/bin/ansible-playbook -i {inventory} {playbook_file} -v"
    app.logger.info(f"cmd: {cmd}")
    # cmd = 'cd {0} && /opt/python3/bin/ansible-playbook -i {1} {2} -v'.format(
    #     os.path.join(app.config["BASE_DIR"], 'app/playbook'), inventory, playbook_file)

    deploy = schema.get_deploy(product)
    fw = open(deploy.result_file, 'w')
    fw.truncate()

    # 更新部署状态
    set_deploy_status(product, 'begin')
    schema.set_product_status(product, 'StartDeploy')

    proc = subprocess.Popen(cmd, shell=True, stderr=fw, stdout=fw)
    app.logger.info(f"Execute Pid: {proc.pid}")

    set_deploy_status(product, 'running')

    app.logger.info(f"process status: {proc.poll()}")
    i = 0
    while proc.poll() is None:
        if i % 10 == 0:
            app.logger.info(f"Excute Running...")
        time.sleep(3)

    set_deploy_status(product, 'finished')
    app.logger.info(f"Excute Finished")


def checkout_log(logfile):
    """
    处理ansible日志输出
    :param logfile:
    :return:
    """
    output = []

    if not logfile:
        return 'Unkown', output

    if os.path.exists(logfile):
        with open(logfile, 'rb') as fr:
            for line in fr:
                if line.strip():
                    output.append(line.strip().decode('utf8'))

    app.logger.info(f"anisble playbook output: {output}")
    state_lst = []
    for line in output:
        if 'ok=' in line and 'changed=' in line and 'unreachable=' in line and 'failed=' in line:
            state_lst.append(True)
            n = int(line.split('unreachable=')[-1].split()[0])
            if n != 0:
                state_lst[-1] = False
            n = int(line.split('failed=')[-1].split()[0])
            if n != 0:
                state_lst[-1] = False

    if len(state_lst) == 0:
        status = 'finished'
    elif all(state_lst):
        status = 'successed'
    elif any(state_lst):
        n = len([state for state in state_lst if not state])
        status = 'failed [{0}]'.format(n)
    else:
        status = 'failed all'
    return status, output


def execute_playbook(product):
    """
    执行 playbook
    :param product:
    :return:
    """
    prod_obj = schema.get_product(product)
    if not prod_obj or prod_obj.status != 'deploy' or prod_obj.deploy.status != 'init':
        app.logger.info(f"Skip Excute Playbook: {product}")
        return
    app.logger.info(f"Start Excute playbook...")
    create_playbook(product)
    deploy = schema.get_deploy(product)
    if not deploy or deploy.status != 'start':
        app.logger.info(f'Execute Skip: {product}')
        return

    try:
        _execute(product)

        deploy = schema.get_deploy(product)
        _status, _ = checkout_log(deploy.result_file)
        set_deploy_status(product, _status)
        schema.set_product_status(product, _status)
        app.logger.info(f'Execute Status: {_status}')

        return _status

    except Exception as ex:
        app.logger.info(f'Execute Failed: {ex}')
        set_deploy_status(product, 'failed')
        schema.set_product_status(product, 'failed')

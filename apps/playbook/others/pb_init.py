#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import json
import hashlib
from collections import defaultdict
from app import app
from app import db, schema, conf, tools


# PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.insert(0, PATH)

def get_playbook_file(product, name):
    path = os.path.join(app.config["BASE_DIR"], 'app/backup/playbook', product)
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, name)


def set_playbook(product, name, data):
    filename = get_playbook_file(product, name)
    with open(filename, 'wb') as f:
        f.write(data)


def get_result_file(product, name):
    """
    playbook log
    :param product:
    :param name:
    :return:
    """
    path = os.path.join(app.config["BASE_DIR"], 'app/playbook/history', product)
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, name)


def gen_vars(product):
    """
    处理rcx和rce license
    :param product:
    :return:
    """
    _vars = {'all': dict(), 'instance': dict(), 'host': dict()}

    for cm in schema.Configmap.query.filter_by(product='common'):
        if cm.name == 'json':
            _vars['all'][cm.key] = json.loads(cm.value)
        else:
            _vars['all'][cm.key] = cm.value

    for cm in schema.Configmap.query.filter_by(product=product):
        if cm.level in ('default', 'global', 'group', 'register'):
            if cm.name == 'json':
                _vars['all'][cm.key] = json.loads(cm.value)
            else:
                _vars['all'][cm.key] = cm.value
        elif cm.level in ('host', 'instance'):
            if cm.name not in _vars[cm.level]:
                _vars[cm.level][cm.name] = dict()
            _vars[cm.level][cm.name][cm.key] = cm.value

    if product == 'im' and 'license' in _vars['all']:
        path = os.path.join(app.config["BASE_DIR"], 'app/playbook/roles/rcx/files')
        license = _vars['all']['license']
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, 'license'), 'w') as fw:
            fw.write(license)
    if product == 'rce' and 'license' in _vars['all']:
        path = os.path.join(app.config["BASE_DIR"], 'app/playbook/roles/rcx-moments/files')
        license = _vars['all']['license']
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, 'license'), 'w') as fw:
            fw.write(license)

    return _vars


def gen_insts(product):
    _product = schema.get_product(product)
    return list(schema.Instance.query.filter_by(product_id=_product.id))


def gen_host(product, pbvars):
    """
    各产品 ansible inventory变量
    :param product:
    :param pbvars:
    :return:
    """
    hosts = dict()
    for host in schema.get_hosts(product=product):
        hosts[host.name] = dict(pbvars['host'][host.name])
        hosts[host.name]['ansible_host'] = host.private_ip
        hosts[host.name]['public_ip'] = host.public_ip
        hosts[host.name]['private_ip'] = host.private_ip
        hosts[host.name]['ansible_user'] = host.user
        if host.password and host.password not in ('None'):
            hosts[host.name]['ansible_ssh_pass'] = host.password
        if host.private_key_file and host.private_key_file not in ('', None,
                                                                   'None'):
            hosts[host.name][
                'ansible_ssh_private_key_file'] = host.private_key_file
    return hosts


def gen_playbook(product, pbvars, insts):
    """
    生成 playbook 文件
    :param product:
    :param pbvars:
    :param insts:
    :return:
    """
    arch = conf.IM_ARCH if product == 'im' else conf.RCE_ARCH

    # Add instance
    temp_pbs = []
    services = set()
    print("{0} - {1} ".format(product, insts))
    for inst in insts:
        pb = dict()

        pb['vars'] = dict(arch[inst.service].get('vars', dict()))
        if inst.name in pbvars['instance']:
            pb['hosts'] = inst.host.name
            pb['vars'].update(pbvars['instance'][inst.name])
        elif inst.service in services:
            continue
        else:
            pb['hosts'] = inst.service
            services.add(inst.service)

        roles = arch[inst.service]['roles']
        if type(roles) == str:
            roles = [roles]
        pb['roles'] = [{'role': role, 'tags': inst.service} for role in roles]

        sort_id = arch[inst.service].get('sort', 999)
        temp_pbs.append((sort_id, pb))

    # print("==== playbook values =====: %s" % json.dumps(temp_pbs, indent=4, ensure_ascii=False))

    playbooks = [pb for _, pb in sorted(temp_pbs, key=lambda x: x[0])]
    if not playbooks:
        playbooks = []

    # Add all
    pb = dict()
    pb['hosts'] = 'all'
    roles = arch['all']['roles']
    if type(roles) == str:
        roles = [roles]
    pb['roles'] = [{'role': role, 'tags': 'all'} for role in roles]
    pb['vars'] = arch['all'].get('vars', dict())
    playbooks.insert(0, pb)

    return playbooks


def gen_hostini(hosts, insts):
    """
    生成 hosts 文件
    :param hosts:
    :param insts:
    :return:
    """
    lines = []
    lines.append('[all]')
    for host, _vars in hosts.items():
        lst = ['{0}={1}'.format(k, v) for k, v in _vars.items()]
        lst = [host] + lst
        lines.append('\t'.join(lst))

    services = defaultdict(set)
    for inst in insts:
        services[inst.service].add(inst.host.name)

    for _group, _hosts in services.items():
        lines.append('')
        lines.append('[{0}]'.format(_group))
        for _host in _hosts:
            lines.append(_host)
    return lines


def set_deploy(product, name):
    """
    部署信息
    :param product:
    :param name:
    :return:
    """
    result = {
        'product': product,
        'name': name,
        'status': 'init',
        'deploy_type': 'ansible',
        'status_time': tools.now()
    }
    result['deploy_file'] = get_playbook_file(product, name)
    result['result_file'] = get_result_file(product, name)
    from app.models import Deploy
    row = Deploy(**result)
    db.session.add(row)
    product = schema.get_product(product)
    product.status = 'deploy'
    product.deploy = row
    db.session.commit()


def init_playbook(product):
    """
    init playbook
    :param product:
    :return:
    """
    prod_obj = schema.get_product(product)
    if not product or prod_obj.status != 'start':
        app.logger.info(f"Skip Init Playbook: <{product}>...")
        return
    app.logger.info(f"Init Playbook: <{product}>...")
    pbvars = gen_vars(product)
    insts = gen_insts(product)
    hosts = gen_host(product, pbvars)
    hostini = gen_hostini(hosts, insts)
    playbooks = gen_playbook(product, pbvars, insts)
    _insts = []

    # print(pbvars, insts, hosts, hostini, playbooks, _insts)
    for inst in insts:
        d = dict()
        d['name'] = inst.name
        d['product'] = inst.product.name
        d['host'] = inst.host.name
        d['service'] = inst.service
        _insts.append(d)
    data = {
        'hosts': hosts,
        'vars': pbvars,
        'insts': _insts,
        'hostini': hostini,
        'playbooks': playbooks,
        'datetime': tools.now().isoformat()
    }
    blob = json.dumps(data).encode('utf-8')
    name = hashlib.md5(blob).hexdigest()
    set_playbook(product, name, blob)
    set_deploy(product, name)

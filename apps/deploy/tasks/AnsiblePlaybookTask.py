#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: AnsiblePlaybookTask.py 
@time: 2020/03/20 22:43
@contact: shu_ke163@163.com
@software:  Door
"""

import os
import re
import sys
import logging
import subprocess
import traceback
from door.celery import app
from django.conf import settings
from apps.deploy.models import DeployModels

logger = logging.getLogger("door")


@app.task(name="tasks.ansible_playbook_api")
def excute_ansible_playbook():
    popen = None

    all_host = DeployModels.objects.filter(status=0)

    if all_host:
        try:
            cmd = f"python {os.path.join(settings.BASE_DIR, 'utils/ansible_playbook_api.py')}"
            popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     universal_newlines=True, close_fds=True, bufsize=1, shell=True)
            logger.info(f"Execute Pid: {popen.pid}")

            while popen.poll() is None:
                print('Excute Running...')
                char = popen.stdout.readlines()
                logger.info(f"ansible playbook info: {char}")

                for row in all_host:
                    row.status = 1
                    row.save()

            stdout, stderr = popen.communicate()
            # sys.stdout.write(stdout)

            print('Excute Finished!')

            for row in all_host:
                row.status = 2
                row.save()

            if popen.poll() != 0:
                err = popen.stderr.readline()
                logger.error(f"Error: {err}")

            return True
        except Exception as e:
            popen.terminate()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logger.error(f"{traceback.print_exc()}")
            logger.error(f"ansible playbook excute failed: {e}")
            for row in all_host:
                row.status = 3
                row.save()
            return False, str(e)

        finally:
            popen.kill()


@app.task(name="tasks.ansible_playbook_shell")
def excute_ansible_playbook_shell(yml_name="local"):
    p = None
    all_host = DeployModels.objects.all()
    try:
        deploy_end = DeployModels.objects.filter(status=3).all()
        if deploy_end:
            DeployModels.objects.filter(status=3).update(status=0)

        cmd = f"ansible-playbook -i inventory/hosts.ini {yml_name}.yml -f 50"
        logger.info(f"cmd: {cmd}")
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True, close_fds=True, bufsize=1, shell=True,
                             cwd=os.path.join(settings.BASE_DIR, "apps/playbook"))

        logger.info(f"Execute Pid: {p.pid}")

        while p.poll() is None:
            print(f"Execute Pid: {p.pid}, status: Running...")
            logger.info(f"Ansible playbook Running and pid is: {p.pid}")
            out = p.stdout.readlines()

            # sys.stdout.write(char)

            for row in all_host:
                row.status = 1
                row.save()

        for line in out:
            logger.info(f"ansible playbook info: {line}")

        if os.path.exists(os.path.join(settings.BASE_DIR, "logs/ansible-playbook.log")):
            os.remove(os.path.join(settings.BASE_DIR, "logs/ansible-playbook.log"))

        with open(os.path.join(settings.BASE_DIR, "logs/ansible-playbook.log"), "w+", encoding="utf-8") as outfile:
            for line in out:
                outfile.write(line)

        logger.info(f"Excute ansible_playbook_shell tasks finished!")

        for item in out:
            if not item:
                continue
            if re.match(r"PLAY RECAP", item):
                index = int(out.index(item))
                result = out[index + 1: -1]
       
        failed_list = []
        for item in result:
           l = item.split()
           failed_list.append(l[5].split("=")[1])

        logger.info(f"ansible playbook excute result: {failed_list}")
        result_set = set(failed_list)
        if len(result_set) == 1 and int(result_set.pop()) == 0:
            for row in DeployModels.objects.all():
                row.status = 2
                row.save()
        else:
            for row in DeployModels.objects.all():
                row.sattus = -1
                row.save()

        if p.poll() != 0:
            err = p.stderr.readlines()
            logger.error(f"Error: {err}")

        return True
    except Exception as e:
        p.terminate()
        logger.error(f"ansible playbook excute failed: {e}")
        for row in DeployModels.objects.all():
            row.status = -1
            row.save()
        return False, str(e)

    finally:
        p.kill()
        return True

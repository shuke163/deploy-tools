#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: __init__.py.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/18 17:55
@software:  Door
"""

import os
import ruamel.yaml
import json
import logging

logger = logging.getLogger("door")

try:
    from django.conf import settings

    BASE_DIR = settings.BASE_DIR
except Exception as e:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(BASE_DIR)


class ParseSvcSort(object):
    """
    解析服务编排文件
    """

    def __init__(self, business):
        self.name = business
        self.business = os.path.join(BASE_DIR, "apps/deploy/conf/arch/{business}.yaml".format(business=business))
        self.base = os.path.join(BASE_DIR, "apps/deploy/conf/arch/base.yaml")
        self.data = self._load()
        self.host_group = list(group for group in self.data.keys())
        logger.info(f"parsing yaml conf, {self.base} {self.business}")

    def _load(self):
        try:
            with open(self.business, mode="r", encoding="utf-8") as config, open(self.base, mode="r",
                                                                                 encoding="utf-8") as base:
                config = ruamel.yaml.safe_load(config)
                base = ruamel.yaml.safe_load(base)
                config.update(base)
                return config
        except IOError as e:
            logger.error(f"{self.business} or {self.base} file not found!")
        except ruamel.yaml.YAMLError as exc:
            logger.error(str(exc))

    def host_group_list(self):
        host_group_list = []
        for group, svc_dict in self.data.items():
            host_group_list.append(
                {"name": group, "sort": svc_dict.get("sort", None), "business": self.name, "description": svc_dict.get(
                    "description", None), "role": ",".join(svc_dict.get("roles", None))})
        return host_group_list

    def get_svc_list(self):
        svc_list = []
        for group, svc_dict in self.data.items():
            svc_list.append(
                {"name": group, "sort": svc_dict.get("sort", None), "business": self.name, "description": svc_dict.get(
                    "description", None), "role": ",".join(svc_dict.get("roles", None))})
        return svc_list

    @property
    def get_svc_sort_list(self):
        return sorted(self.data.items(), key=lambda x: x[1]["sort"])

    @property
    def get_host_group(self):
        return sorted(self.data.keys())

    @property
    def get_all_svc(self):
        return sorted(self.data.keys())


if __name__ == '__main__':
    ret = ParseSvcSort(business="rcx").get_svc_sort_list
    print(json.dumps(ret, indent=4, ensure_ascii=False))

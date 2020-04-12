#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: HandlerVars.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/17 22:01
@software:  Door
"""

import logging
from apps.deploy import models
from config import ConfigParser

logger = logging.getLogger("door")


class ApplicationConfig:
    """
    处理业务线及配置信息
    """

    def __init__(self, name=None, business=None, config="vars.yaml"):
        self.name = name
        self.config = config
        self.business = business
        self.data = ConfigParser(config=config).load()

    @property
    def get_business(self):
        return self.data.keys()

    def get_business_list(self):
        result = []
        for key, val in self.data.items():
            result.append({"name": key, "description": val.get("description", None)})

        return result

    @property
    def read(self):
        if not self.data:
            raise Exception(f"parse {self.config} file error!")
        if self.name is None:
            return self.data
        else:
            return self.data[self.name]

    def write(self, request):
        if not self.data or request is None:
            raise Exception(f"parse {self.config} file error and request is None")

        all_vars_data, post_config_data = self.data, request.data
        all_vars_data["base"]["global"] = post_config_data.pop("global")

        for key, val in all_vars_data[self.business].items():
            for k, v in post_config_data.items():
                if key == k:
                    all_vars_data[self.business][key] = v

        logger.info(f"update config info: {all_vars_data}")
        return all_vars_data


class ConfigMapModel(object):
    """
    更新配置信息入库
    此处有 hard code，可优化
    """

    def __init__(self):
        self.vars = ApplicationConfig().data

    def write(self):
        for key, val in self.vars.items():
            if key == "base":
                for title in ["global", "mysql"]:
                    for item in val.get(title, None):
                        models.ConfigMap.objects.update_or_create(business=key, level="G", title=title,
                                                                  key=item.get("key", None),
                                                                  value=item.get("value", None),
                                                                  isBase=item.get("isBase", None),
                                                                  comment=item.get("comment", None))
            elif key == "rcx":
                for title in ["rcx_rcdb", "rcx_server", "rcx_fileserver", "redis", "nginx", "zookeeper", "mysql"]:
                    for item in val.get(title, None):
                        models.ConfigMap.objects.update_or_create(business=key, level="HG", title=title,
                                                                  key=item.get("key", None),
                                                                  value=item.get("value", None),
                                                                  isBase=item.get("isBase", None),
                                                                  comment=item.get("comment", None))
            elif key == "rce":
                for title in ["rce_rcdb", "elasticsearch", "redis", "nginx", "rcx_moments", "mysql"]:
                    for item in val.get(title, None):
                        models.ConfigMap.objects.update_or_create(business=key, level="HG", title=title,
                                                                  key=item.get("key", None),
                                                                  value=item.get("value", None),
                                                                  isBase=item.get("isBase", None),
                                                                  comment=item.get("comment", None))
            elif key == "rtc":
                for title in ["rtc", "openresty"]:
                    for item in val.get(title, None):
                        models.ConfigMap.objects.update_or_create(business=key, level="HG", title=title,
                                                                  key=item.get("key", None),
                                                                  value=item.get("value", None),
                                                                  isBase=item.get("isBase", None),
                                                                  comment=item.get("comment", None))
            else:
                logger.error(f"Business not Found!")


if __name__ == '__main__':
    c = ConfigMapModel()
    c.write()

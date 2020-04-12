#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: __init__.py.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/06 17:46
@software:  Door
"""

import os
import ruamel.yaml

import logging

logger = logging.getLogger("door")

try:
    from django.conf import settings

    BASE_DIR = settings.BASE_DIR
except Exception as e:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigParser:
    def __init__(self, config="config.yaml"):
        self.file_path = os.path.join(BASE_DIR, f'config/{config}')
        self.file_name = config
        environment = os.getenv("env", "dev")
        logger.info(f"environment: {environment}")

    def load(self):
        try:
            with open(self.file_path, encoding="utf-8") as config:
                data = ruamel.yaml.safe_load(config)
                return data
        except IOError as e:
            logger.info(f"{self.file_name} file not found!")
        except ruamel.yaml.YAMLError as exc:
            logger.error(str(exc))

    @classmethod
    def get(cls, env=None, key=None):
        data = cls().load()
        if data:
            if env and key is None:
                return data.get(env)
            elif env and key:
                section = data.get(env)
                if section is None:
                    raise NotImplementedError
                value = section.get(key)
                if value is None:
                    raise NotImplementedError
                return value
            else:
                return data


class BaseConfig(object):
    """
    base config
    """
    env = "base"
    DEBUG = ConfigParser.get(env, "debug")
    APP = ConfigParser.get(env, "app")
    PROJECT = ConfigParser.get(env, "project")


class DevConfig(BaseConfig):
    """
    dev config
    """
    env = "dev"
    mysql = ConfigParser.get(env, "mysql")
    redis = ConfigParser.get(env, "redis")
    kafka = ConfigParser.get(env, "kafka")


class StageConfig(BaseConfig):
    """
    dev config
    """
    env = "stage"
    mysql = ConfigParser.get(env, "mysql")
    redis = ConfigParser.get(env, "redis")
    kafka = ConfigParser.get(env, "kafka")


class ProdConfig(BaseConfig):
    """
    product config
    """
    env = "prod"
    mysql = ConfigParser.get(env, "mysql")
    redis = ConfigParser.get(env, "redis")
    kafka = ConfigParser.get(env, "kafka")


config = {
    'dev': DevConfig,
    'stage': StageConfig,
    'prod': ProdConfig,
}

if __name__ == '__main__':
    print(config["dev"]().env, config["dev"]().DEBUG, config["dev"]().PROJECT, config["dev"]().mysql,
          config["dev"]().redis, config["dev"]().kafka)

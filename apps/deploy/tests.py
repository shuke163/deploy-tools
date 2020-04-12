from django.test import TestCase
from apps.deploy.models import Role


# Create your tests here.


def create_roles():
    roles_list = [
        {"name": "redis", "description": "redis session存储"},
        {"name": "mysql", "description": "数据库服务"},
        {"name": "elasticsearch", "description": "rce搜素服务"},

        {"name": "zookeeper", "description": "zk中间件"},
        {"name": "rcdb", "description": "rcdb"},
        {"name": "nginx", "description": "nginx web服务器"},
        {"name": "rcx-management", "description": "rcx管理后台"},
        {"name": "fastdfs", "description": "fastdfs"},
        {"name": "rcx-fileserver", "description": "rcx-fileserver文件服务"},
        {"name": "rcx", "description": "rcx服务"},
        {"name": "rcx-db", "description": "rcx-db"},
        {"name": "tproxy-rcx", "description": "tproxy-rcx代理服务"},
        {"name": "dc-agent", "description": "dc-agent"},
        {"name": "loghub", "description": "loghub"},

        {"name": "install-python", "description": "初始化python环境"},
        {"name": "systemconf", "description": "初始化系统配置"},
        {"name": "supervisord", "description": "supervisord进程管理工具"},
        {"name": "jre", "description": "java环境"},

        {"name": "initdb", "description": "初始化rce数据库 "},
        {"name": "tomcat", "description": "tomcat容器服务"},
        {"name": "rce", "description": "rce服务"},
        {"name": "rce-rcx", "description": "rce-im前端页面"},
        {"name": "erp-work", "description": "工作圈前端页面"},
        {"name": "rcx-moments", "description": "工作圈服务"},

        {"name": "rtc", "description": "rtc音视频服务"},
        {"name": "openresty", "description": "openresty服务"},
    ]

    queryset_list = []
    for item in roles_list:
        queryset_list.append(Role(name=item["name"], description=item["description"]))

    Role.objects.bulk_create(queryset_list)

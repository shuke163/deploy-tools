import ast
from django.db import models
from utils.base_models import BaseTimestampModel
#from apps.host.models import Host


class JSONField(models.TextField):
    description = "Json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            value = {}
        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_save(value)


class BusinessLine(BaseTimestampModel):
    """
    业务线信息表
    """
    name = models.CharField(max_length=16, null=False, blank=True, verbose_name="业务线名称")
    is_active = models.BooleanField(null=False, default=False, blank=True, verbose_name="是否激活")
    sort = models.SmallIntegerField(null=True, blank=True, verbose_name="部署顺序")
    description = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name="描述信息")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "weops_business"
        verbose_name = "业务线信息表"
        verbose_name_plural = "业务线信息表"


# class Role(BaseTimestampModel):
#     """
#     ansible role
#     """
#     name = models.CharField(max_length=32, unique=True, null=False, verbose_name="Ansible role名称")
#     description = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name="描述信息")
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table = "weops_role"
#         verbose_name = "role信息表"
#         verbose_name_plural = "role信息表"


class Service(BaseTimestampModel):
    """
    服务信息表
    """

    name = models.CharField(max_length=32, blank=True, verbose_name="服务名称")
    sort = models.SmallIntegerField(null=True, blank=True, verbose_name="部署顺序")
    description = models.CharField(max_length=32, default=None, null=True, blank=True, verbose_name="描述信息")
    role = models.CharField(max_length=32, null=True, blank=True, verbose_name='角色列表')

    business = models.ForeignKey(BusinessLine, related_name='bus', null=True, blank=True, on_delete=models.CASCADE,
                                 verbose_name='关联的业务线')

    # role = models.ForeignKey(Role, related_name='roles', null=True, blank=True, on_delete=models.CASCADE,
    #                          verbose_name="关联的role")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "weops_service"
        verbose_name = "服务信息表"
        verbose_name_plural = "服务信息表"
        unique_together = ('name', 'business')


#class InstanceInfo(BaseTimestampModel):
#    """
#    实例信息表
#    """
#
#    STATUS_CHOICES = (
#        (0, 'uninstall'),
#        (1, 'init'),
#        (2, 'install-ing'),
#        (3, 'done')
#    )

#   name = models.CharField(max_length=16, null=False, blank=True, verbose_name="实例名称")
#    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0, verbose_name="实例状态")

#    host = models.ManyToManyField(Host, related_name='hosts', verbose_name='关联的主机')

#    @property
#    def get_status(self, obj):
#        return obj.get_status_display()

#    @property
#    def get_hostname(self):
#        return self.host.hostname

#    @property
#    def get_host_list(self):
#        return self.host.values('hostname', 'private_ip', 'public_ip').all()

#    def __str__(self):
#        return self.name

#    class Meta:
#        db_table = "weops_instance_info"
#        verbose_name = "实例信息表"
#        verbose_name_plural = "实例信息表"
#        unique_together = ('name', 'status')


class ResourceConf(BaseTimestampModel):
    """
    资源配置表
    """
    cpu = models.CharField(max_length=8, default="8c", blank=True, verbose_name="CPU核数")
    mem = models.CharField(max_length=12, default="16g", blank=True, verbose_name="内存")
    disk = models.CharField(max_length=12, default="100g", null=True, blank=True, verbose_name="磁盘空间")
    num = models.SmallIntegerField(null=True, blank=True, verbose_name="主机数量")

    service = models.ForeignKey(Service, related_name='svc', null=True, blank=True, on_delete=models.CASCADE)
    business = models.ForeignKey(BusinessLine, related_name='bus_line', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.service.name

    class Meta:
        db_table = "weops_resource_conf"
        verbose_name = "资源配置表"
        verbose_name_plural = "资源配置表"


class DeployModels(BaseTimestampModel):
    """
    部署模型
    """

    STATUS_CHOICES = (
        (0, 'STARTED'),
        (1, 'PENDING'),
        (-1, 'FAILED'),
        (2, 'SUCCSESS'),
        (3, 'RETRY')
    )

    server_name = models.CharField(max_length=16, null=False, blank=True, verbose_name="服务名称")
    hostname = models.CharField(max_length=32, null=False, blank=True, verbose_name="主机名")
    business = models.CharField(max_length=16, null=False, blank=True, verbose_name="业务线")
    private_ip = models.GenericIPAddressField(max_length=16, null=True, blank=True, verbose_name="私有IP")
    external_ip = models.GenericIPAddressField(max_length=16, null=True, blank=True, verbose_name="公有IP")
    cpu = models.CharField(max_length=8, null=True, blank=True, verbose_name="CPU核数")
    mem = models.CharField(max_length=8, null=True, blank=True, verbose_name="内存")
    disk = models.CharField(max_length=8, null=True, blank=True, verbose_name="磁盘空间")
    instance_name = models.CharField(max_length=32, null=True, blank=True, verbose_name="实例名称")
    description = models.CharField(max_length=128, null=True, blank=True, verbose_name="说明")

    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0, null=False, blank=True, verbose_name="部署状态")

    def __str__(self):
        return self.server_name

    class Meta:
        db_table = "weops_deploy_models"
        verbose_name = "部署模型"
        verbose_name_plural = "部署模型表"


class GlobalVars(BaseTimestampModel):
    """
    全局变量表
    """
    business = models.CharField(max_length=8, null=False, blank=True, verbose_name="业务线")
    key = models.CharField(max_length=16, null=False, blank=True, verbose_name="key")
    value = models.CharField(max_length=16, null=False, blank=True, verbose_name="value")
    description = models.CharField(max_length=128, null=True, blank=True, verbose_name="说明")

    def __str__(self):
        return f"self.key | self.value"

    class Meta:
        db_table = "weops_global_vars"
        verbose_name = "全局变量"
        verbose_name_plural = "全局变量表"


class ConfigMap(BaseTimestampModel):
    """
    配置信息表
    """
    HOST = "host"
    HGROUP = "group"
    GLOBAL = "global"
    ROLE = "role"

    LEVEL_CHOICES = (
        ("H", HOST),
        ("HG", HGROUP),
        ("G", GLOBAL),
        ("R", ROLE),
    )

    business = models.CharField(max_length=12, null=False, blank=True, default="rcx", verbose_name="业务线")
    level = models.CharField(max_length=8, choices=LEVEL_CHOICES, default="G", verbose_name="配置项级别")
    title = models.CharField(max_length=32, null=True, blank=True, verbose_name="配置项标题")
    key = models.CharField(max_length=32, null=True, blank=True, verbose_name="配置项key")
    value = models.CharField(max_length=32, null=True, blank=True, verbose_name="配置项value")
    isBase = models.BooleanField(default=False, null=True, blank=True, verbose_name="是否是基础配置")
    comment = models.CharField(max_length=32, null=True, blank=True, verbose_name="描述信息")

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

    @property
    def row_to_dict(self, obj):
        ret = dict()
        ret["business"] = obj.business
        ret["level"] = obj.level
        ret["title"] = obj.title
        ret["key"] = obj.key
        ret["value"] = obj.value
        ret["isBase"] = obj.isBase
        ret["comment"] = obj.comment
        return ret

    def __str__(self):
        return "{business}|{level}|{title}|{key}|{value}|{isBase}|{comment}".format(business=self.business,
                                                                                    level=self.level,
                                                                                    title=self.title, key=self.key,
                                                                                    value=self.value,
                                                                                    isBase=self.isBase,
                                                                                    comment=self.comment)

    class Meta:
        db_table = "weops_configmap"
        verbose_name = "配置信息表"
        verbose_name_plural = "配置信息表"

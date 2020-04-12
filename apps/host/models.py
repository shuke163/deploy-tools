from django.db import models
from utils.base_models import BaseTimestampModel


class Host(BaseTimestampModel):
    """
    主机信息表
    """
    hostname = models.CharField(max_length=32, unique=True, blank=True, verbose_name="主机名")
    private_ip = models.GenericIPAddressField(max_length=16, null=True, blank=True, verbose_name="私有IP")
    public_ip = models.GenericIPAddressField(max_length=16, null=True, blank=True, verbose_name="公有IP")
    user = models.CharField(max_length=12, null=True, blank=True, verbose_name="ssh 用户名")
    password = models.CharField(max_length=32, null=True, blank=True, verbose_name="ssh 密码")
    private_key_file = models.CharField(max_length=32, null=True, blank=True, default="~/.ssh/id_rsa",
                                        verbose_name="ssh密钥文件")
    # private_key_pwd = models.CharField(max_length=32, null=True, blank=True, verbose_name="ssh密钥文件密码")

    group = models.ManyToManyField('HostGroup', related_name='groups', verbose_name="关联的主机组")

    @property
    def get_group(self):
        return self.group.name

    @property
    def get_group_list(self):
        return self.group.values('name', 'description').all()

    def __str__(self):
        return self.hostname

    class Meta:
        db_table = "weops_host"
        verbose_name = "主机信息表"
        verbose_name_plural = "主机信息表"


class HostGroup(BaseTimestampModel):
    """
    主机组表
    """
    name = models.CharField(max_length=32, blank=True, verbose_name="主机组名")
    description = models.CharField(max_length=64, default=None, null=True, blank=True, verbose_name="描述信息")

    business = models.CharField(max_length=12, null=False, blank=True, verbose_name="业务线")

    super_group = models.ForeignKey('self', related_name='s_group', null=True, blank=True, on_delete=models.CASCADE,
                                    verbose_name="关联的父组")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "weops_group"
        verbose_name = "主机组表"
        verbose_name_plural = "主机组信息表"


class Cmdb(BaseTimestampModel):
    """
    CMDB 主机信息表
    """

    hostname = models.CharField(max_length=32, unique=True, null=False, blank=True, verbose_name="主机名")
    fqdn = models.CharField(max_length=32, null=False, blank=True, verbose_name="fqdn")
    cpu = models.CharField(max_length=8, null=False, verbose_name="cpu核数")
    memory = models.CharField(max_length=8, null=False, verbose_name="内存")
    disk = models.CharField(max_length=8, null=False, verbose_name="磁盘空间")
    disk_format = models.CharField(max_length=8, null=False, default="ext4", verbose_name="磁盘格式")
    mount_point = models.CharField(max_length=8, null=False, default="/data", verbose_name="挂载点")
    ipv4 = models.GenericIPAddressField(max_length=16, null=False, verbose_name="ip地址")
    arch = models.CharField(max_length=8, null=False, verbose_name="OS架构")
    os_type = models.CharField(max_length=8, null=False, verbose_name="OS类型")
    os_version = models.CharField(max_length=8, null=False, verbose_name="OS版本")
    machine_id = models.CharField(max_length=36, null=False, verbose_name="机器ID")
    macaddress = models.CharField(max_length=36, null=False, verbose_name="MAC地址")
    kernel_info = models.CharField(max_length=36, null=False, verbose_name="kernel信息")
    virtualization_type = models.CharField(max_length=36, null=False, verbose_name="虚拟化类型")

    # host = models.OneToOneField(Host, related_name='hc', default=None, on_delete=models.CASCADE,
    #                             verbose_name='关联的主机')

    def __str__(self):
        return str(self.hostname)

    class Meta:
        db_table = "weops_cmdb"
        verbose_name = "cmdb资产信息表"
        verbose_name_plural = "cmdb资产信息表"


class SvcValidateModel(BaseTimestampModel):
    """
    service check
    """

    STATE_CHOICE = (
        (0, 'STOPPED'),
        (10, 'STARTING'),
        (20, 'RUNNING'),
        (30, 'BACKOFF'),
        (40, 'STOPPING'),
        (100, 'EXITED'),
        (200, 'FATAL'),
        (1000, 'UNKNOWN')
    )

    server_name = models.CharField(max_length=16, null=False, blank=True, verbose_name="服务名称")
    hostname = models.CharField(max_length=32, null=False, blank=True, verbose_name="主机名")
    business = models.CharField(max_length=16, null=False, blank=True, verbose_name="业务线")
    private_ip = models.GenericIPAddressField(max_length=16, null=True, blank=True, verbose_name="私有IP")
    external_ip = models.GenericIPAddressField(max_length=16, null=True, blank=True, verbose_name="公有IP")
    instance_name = models.CharField(max_length=32, null=True, blank=True, verbose_name="实例名称")

    # supervisor service state info
    name = models.CharField(max_length=16, null=False, blank=True, verbose_name="Name of the process")
    group = models.CharField(max_length=16, null=False, blank=True, verbose_name="Name of the process’ group")
    now = models.CharField(max_length=16, null=False, blank=True,
                           verbose_name="UNIX timestamp of the current time, which can be used to calculate process up-time.")
    start = models.CharField(max_length=16, null=False, blank=True,
                             verbose_name="UNIX timestamp of when the process was started")
    stop = models.CharField(max_length=16, null=False, blank=True,
                            verbose_name="UNIX timestamp of when the process last ended, or 0 if the process has never been stopped.")
    pid = models.SmallIntegerField(null=False, blank=True,
                                   verbose_name="UNIX process ID (PID) of the process, or 0 if the process is not running.")
    exitstatus = models.SmallIntegerField(null=False, blank=True,
                                          verbose_name="Exit status (errorlevel) of process, or 0 if the process is still running.")
    spawnerr = models.CharField(max_length=64, null=True, blank=True,
                                verbose_name="Description of error that occurred during spawn, or empty string if none.")
    logfile = models.CharField(max_length=64, null=False, blank=True, verbose_name="stdout_logfile")
    stdout_logfile = models.CharField(max_length=64, null=False, blank=True,
                                      verbose_name="Absolute path and filename to the STDOUT logfile")
    stderr_logfile = models.CharField(max_length=64, null=False, blank=True,
                                      verbose_name="Absolute path and filename to the STDOUT logfile")
    state = models.SmallIntegerField(choices=STATE_CHOICE, null=False, blank=True,
                                     verbose_name="String description of state, see Process States.")
    statename = models.CharField(max_length=64, null=False, blank=True,
                                 verbose_name="String description of state, see Process States.")
    description = models.CharField(max_length=32, null=False, blank=True,
                                   verbose_name="If process state is running description’s value is process_id and uptimed.")

    def __str__(self):
        return f"{self.server_name}|{self.pid}|{self.statename}"

    class Meta:
        db_table = "weops_svc_check"
        verbose_name = "服务验证"
        verbose_name_plural = "服务验证表"


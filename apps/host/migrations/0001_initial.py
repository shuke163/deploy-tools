# Generated by Django 2.2.6 on 2020-04-14 09:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cmdb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_time', models.DateTimeField(auto_now=True, null=True)),
                ('hostname', models.CharField(blank=True, max_length=32, unique=True, verbose_name='主机名')),
                ('fqdn', models.CharField(blank=True, max_length=32, verbose_name='fqdn')),
                ('cpu', models.CharField(max_length=8, verbose_name='cpu核数')),
                ('memory', models.CharField(max_length=8, verbose_name='内存')),
                ('disk', models.CharField(max_length=8, verbose_name='磁盘空间')),
                ('disk_format', models.CharField(default='ext4', max_length=8, verbose_name='磁盘格式')),
                ('mount_point', models.CharField(default='/data', max_length=8, verbose_name='挂载点')),
                ('ipv4', models.GenericIPAddressField(verbose_name='ip地址')),
                ('arch', models.CharField(max_length=8, verbose_name='OS架构')),
                ('os_type', models.CharField(max_length=8, verbose_name='OS类型')),
                ('os_version', models.CharField(max_length=8, verbose_name='OS版本')),
                ('machine_id', models.CharField(max_length=36, verbose_name='机器ID')),
                ('macaddress', models.CharField(max_length=36, verbose_name='MAC地址')),
                ('kernel_info', models.CharField(max_length=36, verbose_name='kernel信息')),
                ('virtualization_type', models.CharField(max_length=36, verbose_name='虚拟化类型')),
            ],
            options={
                'verbose_name': 'cmdb资产信息表',
                'verbose_name_plural': 'cmdb资产信息表',
                'db_table': 'weops_cmdb',
            },
        ),
        migrations.CreateModel(
            name='SvcValidateModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_time', models.DateTimeField(auto_now=True, null=True)),
                ('server_name', models.CharField(blank=True, max_length=16, verbose_name='服务名称')),
                ('hostname', models.CharField(blank=True, max_length=32, verbose_name='主机名')),
                ('business', models.CharField(blank=True, max_length=16, verbose_name='业务线')),
                ('private_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='私有IP')),
                ('external_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='公有IP')),
                ('instance_name', models.CharField(blank=True, max_length=32, null=True, verbose_name='实例名称')),
                ('name', models.CharField(blank=True, max_length=16, verbose_name='Name of the process')),
                ('group', models.CharField(blank=True, max_length=16, verbose_name='Name of the process’ group')),
                ('now', models.CharField(blank=True, max_length=16, verbose_name='UNIX timestamp of the current time, which can be used to calculate process up-time.')),
                ('start', models.CharField(blank=True, max_length=16, verbose_name='UNIX timestamp of when the process was started')),
                ('stop', models.CharField(blank=True, max_length=16, verbose_name='UNIX timestamp of when the process last ended, or 0 if the process has never been stopped.')),
                ('pid', models.SmallIntegerField(blank=True, verbose_name='UNIX process ID (PID) of the process, or 0 if the process is not running.')),
                ('exitstatus', models.SmallIntegerField(blank=True, verbose_name='Exit status (errorlevel) of process, or 0 if the process is still running.')),
                ('spawnerr', models.CharField(blank=True, max_length=64, null=True, verbose_name='Description of error that occurred during spawn, or empty string if none.')),
                ('logfile', models.CharField(blank=True, max_length=64, verbose_name='stdout_logfile')),
                ('stdout_logfile', models.CharField(blank=True, max_length=64, verbose_name='Absolute path and filename to the STDOUT logfile')),
                ('stderr_logfile', models.CharField(blank=True, max_length=64, verbose_name='Absolute path and filename to the STDOUT logfile')),
                ('state', models.SmallIntegerField(blank=True, choices=[(0, 'STOPPED'), (10, 'STARTING'), (20, 'RUNNING'), (30, 'BACKOFF'), (40, 'STOPPING'), (100, 'EXITED'), (200, 'FATAL'), (1000, 'UNKNOWN')], verbose_name='String description of state, see Process States.')),
                ('statename', models.CharField(blank=True, max_length=64, verbose_name='String description of state, see Process States.')),
                ('description', models.CharField(blank=True, max_length=32, verbose_name='If process state is running description’s value is process_id and uptimed.')),
            ],
            options={
                'verbose_name': '服务验证',
                'verbose_name_plural': '服务验证表',
                'db_table': 'weops_svc_check',
            },
        ),
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_time', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=32, verbose_name='主机组名')),
                ('description', models.CharField(blank=True, default=None, max_length=64, null=True, verbose_name='描述信息')),
                ('business', models.CharField(blank=True, max_length=12, verbose_name='业务线')),
                ('super_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='s_group', to='host.HostGroup', verbose_name='关联的父组')),
            ],
            options={
                'verbose_name': '主机组表',
                'verbose_name_plural': '主机组信息表',
                'db_table': 'weops_group',
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_time', models.DateTimeField(auto_now=True, null=True)),
                ('hostname', models.CharField(blank=True, max_length=32, unique=True, verbose_name='主机名')),
                ('private_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='私有IP')),
                ('public_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='公有IP')),
                ('user', models.CharField(blank=True, max_length=12, null=True, verbose_name='ssh 用户名')),
                ('password', models.CharField(blank=True, max_length=32, null=True, verbose_name='ssh 密码')),
                ('private_key_file', models.CharField(blank=True, default='~/.ssh/id_rsa', max_length=32, null=True, verbose_name='ssh密钥文件')),
                ('group', models.ManyToManyField(related_name='groups', to='host.HostGroup', verbose_name='关联的主机组')),
            ],
            options={
                'verbose_name': '主机信息表',
                'verbose_name_plural': '主机信息表',
                'db_table': 'weops_host',
            },
        ),
    ]

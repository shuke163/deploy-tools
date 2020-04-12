from django.contrib import admin
from apps.host import models


class HostAdmin(admin.ModelAdmin):
    search_fields = ('hostname',)

    readonly_fields = ('hostname',)

    def host_group(self, obj):
        return obj.group.name

    list_display = ['hostname', 'private_ip', 'public_ip', 'user', 'password', 'private_key_file', 'host_group']


class HostGroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    # readonly_fields = ('name',)

    def super_group(self, obj):
        return obj.super_group.name

    list_display = ['name', 'description', 'super_group']


class CmdbAdmin(admin.ModelAdmin):
    search_fields = ('hostname',)

    list_display = ['hostname', 'fqdn', 'cpu', 'memory', 'disk', 'ipv4', 'arch', 'os_type', 'os_version', 'machine_id',
                    'macaddress', 'kernel_info', 'virtualization_type', ]


admin.site.register(models.Host, HostAdmin)
admin.site.register(models.HostGroup, HostGroupAdmin)
admin.site.register(models.Cmdb, CmdbAdmin)

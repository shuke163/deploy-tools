from django.contrib import admin

from apps.deploy import models


class BusinessLineAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', ]


class ServiceAdmin(admin.ModelAdmin):
    fk_fields = ('business_id',)
    list_filter = ('name', 'business', 'role',)

    search_fields = ('name',)

    # readonly_fields = ('sort',)

    def business(self, obj):
        return obj.business.name

    def roles(self, obj):
        return [role.name for role in obj.role.all()]

    list_display = ['name', 'description', 'sort', 'business', 'roles']


class ResourceAdmin(admin.ModelAdmin):
    search_fields = ('register',)

    list_display = ['register', 'online', 'msg_qps', 'text_qps', 'voip_qps', 'is_ha', 'description', ]


class ResourceConfAdmin(admin.ModelAdmin):
    search_fields = ('service',)

    def service(self, obj):
        return obj.service.name

    def business(self, obj):
        return obj.business.name

    list_display = ['cpu', 'mem', 'disk', 'num', 'service', 'business']


class RoleAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    list_display = ['name', 'description', ]


class ConfigMapAdmin(admin.ModelAdmin):
    search_fields = ('business', 'title', 'key', 'value')
    list_display = ['business', 'level', 'title', 'key', 'value', 'isBase', 'comment']


admin.site.register(models.BusinessLine, BusinessLineAdmin)
admin.site.register(models.Service, ServiceAdmin)
# admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.ResourceConf, ResourceConfAdmin)
admin.site.register(models.ConfigMap, ConfigMapAdmin)

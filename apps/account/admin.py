from django.contrib import admin
from apps.account import models

admin.sites.site_header = "后台管理"

admin.site.register(models.Account)

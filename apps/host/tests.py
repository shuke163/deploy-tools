# from django.test import TestCase


import os

from apps.host.models import Host, HostGroup

rcx_obj = HostGroup.objects.filter(name="rcx").first()
print(rcx_obj)

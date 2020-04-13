'''
@Author: your name
@Date: 2020-04-13 12:02:08
@LastEditTime: 2020-04-13 12:19:21
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /deploy-backend/door/wsgi.py
'''
"""
WSGI config for door backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'door.settings')

application = get_wsgi_application()

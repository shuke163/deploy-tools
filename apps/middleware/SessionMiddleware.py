#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: __init__.py.py
@time: 2019/10/25 11:56
@contact: shu_ke163@163.com
@software:  Door
"""


from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse


class ClearSessionMiddleware(MiddlewareMixin):
    """
    session middleware
    """
    def process_request(self, request):
        print("This is session -> HttpRequest")

    def process_response(self, request, response):
        print("This is session -> HttpResponse")
        return response 

    def process_view(self, request, view_func, view_args, view_kwargs):
        '''
        :param request: 浏览器发来的 request 请求对象
        :param view_func: 将要执行的视图函数的名字
        :param view_args: 将要执行的视图函数的位置参数
        :param view_kwargs: 将要执行的视图函数的关键字参数
        :return:
        '''
        print("This is session ->  process_view func")
        print(view_func, type(view_func))

#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: listen.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/12 09:08
@software:  Door
"""

import os

import socket


def IsOpen(ip, port):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect((ip, int(port)))
        sk.shutdown(2)
        print('%d is open' % port)
        return True

    except:
        print('%d is down' % port)
        return False


if __name__ == '__main__':
    IsOpen('127.0.0.1', 6380)

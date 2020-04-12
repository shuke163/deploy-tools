#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: udp.py 
@time: 2020/03/26 17:38
@contact: shu_ke163@163.com
@software:  Door
"""
#
# import socket
#
# IPs = ['ntp.ntsc.ac.cn', ]
# Ports = [123, ]
# for ip in IPs:
#     for port in Ports:
#         ADDR = (ip, port)
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.settimeout(3)
#
#         result = s.connect_ex(ADDR)
#         print(result)
#
#         if result == 0:
#             print("The Server IP: {} , Port {} has been used".format(ip, port))
#         s.close()



import socket

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()
    finally:
        s.close()

    print(ip)
    return ip

get_host_ip()


#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: listen_port.py 
@time: 2020/04/01 03:47
@contact: shu_ke163@163.com
@software:  door
"""

import os
import sys
import socket
import select
import json
import traceback
from django.conf import settings
import logging

PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "door.settings")

import django

django.setup()

logger = logging.getLogger("door")

log_filename = f'{settings.BASE_LOG_DIR}/check_ports.log'

logging.basicConfig(
    level=getattr(logging, 'DEBUG', logging.DEBUG),
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=log_filename, filemode='a',
)

class ListenPorts(object):
    """
    listen ports
    """

    def __init__(self):
        self.listen_port_list = self._get_listen_port()

    def _get_listen_port(self):
        with open(os.path.join(settings.BASE_DIR, "config/ports.json"), mode="r", encoding="utf-8") as p:
            listen_port_list = json.load(p)
            return listen_port_list

    def listen_mutil_port(self):
        try:
            servers = []
            for item in self.listen_port_list:
                for k, v in item.items():
                    if "protocol" in k and "tcp" in v:
                        bind = (item["addr"], int(item["port"]))
                        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        server.bind(bind)
                        server.listen(5)
                        servers.append(server)
                    elif "protocol" in k and "udp" in v:
                        bind = (item["addr"], int(item["port"]))
                        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        server.bind(bind)
                        servers.append(server)

            logging.info(f"listen server list: {servers}")

            while True:
                readable, _, _ = select.select(servers, [], [])
                print("000000000000000000000000000000000", readable)
                logging.info(f"select readable conn: {readable}")
                ready_server = readable[0]
                for s in servers:
                    if s in readable:
                        if str(ready_server.type) == "SocketKind.SOCK_DGRAM":
                            data, client = ready_server.recvfrom(1024)
                            if data:
                                logging.info(f"udp protocol...")
                                logging.info(f"data: {data}")
                                logging.info(f"server addr: {readable}, client addr: {s}")
                                ready_server.settimeout(30)
                                ready_server.sendto(data, client)
                                break
                        elif str(ready_server.type) == "SocketKind.SOCK_STREAM":
                            conn, addr = ready_server.accept()
                            conn.settimeout(30)
                            data = conn.recv(1024)
                            if data:
                                logging.info(f"tcp protocol...")
                                logging.info(f"data: {data}")
                                logging.info(f"server addr: {readable}, client addr: {addr}")
                                conn.send(bytes(str(data), encoding="utf-8"))
                                conn.settimeout(30)
                                conn.close()
                            break
                continue
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(f"{traceback.format_exception(exc_type, exc_value, exc_traceback)}")
            logging.error(f"{traceback.print_exc()}")


if __name__ == '__main__':
    l = ListenPorts()
    l.listen_mutil_port()


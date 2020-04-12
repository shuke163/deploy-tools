#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: port.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/03/08 15:10
@software:  Door
"""

import sys
import logging
import socketserver
from multiprocessing import Process


def get_logger():
    log_path = "/tmp/listen_port.log"

    logger = logging.getLogger(__name__)

    # StreamHandler

    stream_handler = logging.StreamHandler(sys.stdout)

    stream_handler.setLevel(level=logging.WARN)

    logger.addHandler(stream_handler)

    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s',
                                  datefmt='%Y/%m/%d %H:%M:%S')

    logger.setLevel(level=logging.INFO)

    handler = logging.FileHandler(log_path)

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = get_logger()


class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        conn = self.request
        while True:
            data = str(conn.recv(1024), encoding="utf-8").strip()
            logger.info(f"{conn}, request: {data}")
            if data == "exit" or data == "quit":
                conn.close()
                break

            conn.sendall(b'server: ')


def main():
    server1 = socketserver.ForkingTCPServer(('127.0.0.1', 8400), MyServer)
    server1.max_children = 1

    server2 = socketserver.ForkingTCPServer(('127.0.0.1', 9400), MyServer)
    server2.max_children = 1
    p = Process(target=server2.serve_forever, args=())
    p.start()

    # server1需放在p.start后启动不然会阻塞进程，server2无法启动
    server1.serve_forever()

    p.join()


if __name__ == '__main__':
    main()

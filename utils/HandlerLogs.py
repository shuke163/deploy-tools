#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: HandlerLogs.py 
@time: 2020/03/20 20:08
@contact: shu_ke163@163.com
@software:  Door
"""

import re
import os
import sys
import json
import logging
from xlsxwriter import Workbook


def get_logger():
    log_path = "/tmp/output.log"

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


def list_all_files(rootdir):
    logs_list = []
    _files = []
    l1 = os.listdir(rootdir)
    for i in range(0, len(l1)):
        path = os.path.join(rootdir, l1[i])
        if os.path.isdir(path):
            _files.extend(list_all_files(path))
        if os.path.isfile(path):
            _files.append(path)

    for file in _files:
        searchObj = re.search(r'\d-*.log$', file, re.M | re.I)
        if searchObj:
            # print(file)
            logs_list.append(file)

    return list(set(logs_list))


class HandlerLogs:
    def __init__(self, path, excel_name):
        self.path = path
        self.logs_list = list_all_files(path)
        self.excel_name = excel_name
        self.papers = []
        self.n = 1000
        self.logs_split_list = [self.logs_list[i:i + self.n] for i in range(0, len(self.logs_list), self.n)]

    def handler_logs(self):

        for row in self.logs_split_list:
            for item in row:
                self.papers = []
                for file in item:
                    with open(file, "r", encoding="utf-8") as f:
                        for line in f.readlines():
                            dic = json.loads(line)
                            self.papers.append(dic)

                self.write_excel(players=self.papers, )

        # print(json.dumps(self.papers, indent=4, ensure_ascii=False))

        return self.papers

    def write_excel(self, players):

        ordered_list = ["timestamp", "fromUserId"]

        wb = Workbook(self.excel_name)
        ws = wb.add_worksheet("msgLogs")

        first_row = 0
        for header in ordered_list:
            col = ordered_list.index(header)
            ws.write(first_row, col, header)

        row = 1
        for player in players:
            for _key, _value in player.items():

                if _key not in ordered_list:
                    continue

                logger.info(f"{_key}: {_value}")

                col = ordered_list.index(_key)
                ws.write(row, col, _value)
            row += 1

        wb.close()


if __name__ == '__main__':
    log = HandlerLogs(path="/tmp/rcx-server/rcx-server.inst-0", excel_name="logs.xlsx")
    logs_list = log.handler_logs()
    log.write_excel(players=logs_list)

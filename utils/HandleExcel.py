#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: HandleExcel.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/09 11:02
@software:  Door
"""

import sys
import re
import os
import xlrd
import json
import logging
import traceback

from collections import defaultdict

logger = logging.getLogger("door")

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads/物料_V1_20200302.xlsx')


class ReadExcel(object):
    """
    处理excel表格
    """

    def __init__(self, excel_name="物料_V1_20200302.xlsx"):
        self.excel_name = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                       f'uploads/{excel_name}')
        self.data = xlrd.open_workbook(self.excel_name)
        self.workbook = xlrd.open_workbook(self.excel_name)
        self.sheets = self.data.nsheets
        self.sheet_list = self.get_all_sheets()
        self._exce_dict = None
        self.business = None
        self.title = ["server_name", "private_ip", "external_ip", "cpu", "mem", "disk", "description"]

    def get_all_sheets(self):
        """
        获取所有的sheets
        :return:
        """
        sheet_list = self.data.sheet_names()
        sheets_list = list()
        for index, sheet in enumerate(sheet_list, start=0):
            sheet_dict = dict()
            sheet_dict["index"] = index
            sheet_dict["name"] = sheet.split("_")[0].lower()
            sheets_list.append(sheet_dict)
        if len(sheet_list) != 3:
            logger.error(f"sheet num is not equal to 3, please check!")

        logger.info(f"sheet list: {sheets_list}")
        return sheets_list

    def resource_sheet(self):
        sheet_index = 0
        sheet = self.data.sheet_by_index(sheet_index)
        sheet_is_load = self.data.sheet_loaded(sheet_name_or_index=sheet_index)
        if sheet_is_load:
            sheet_total_row_num = sheet.nrows
            for line in range(sheet_total_row_num):
                if int(line) == 0:
                    title = [item.strip() for item in sheet.row_values(rowx=line)]
                    continue
                row = self._float_to_num(sheet.row_values(rowx=line))

            resource_sheet_list = [dict(zip(title, row)), ]
            return resource_sheet_list

    def parse_deploy_model(self):
        """
        解析部署模型sheet
        :return:
        """
        sheet_index = 0
        sheet = self.data.sheet_by_index(sheet_index)
        sheet_is_load = self.data.sheet_loaded(sheet_name_or_index=sheet_index)
        if sheet_is_load:
            sheet_total_row_num = sheet.nrows

            model_list = list()
            for line in range(1, sheet_total_row_num):
                row = sheet.row_values(rowx=line)
                
                svc_name, ip_addr = row[0], row[1]
                
                pattern = re.compile(r'^[a-z]+_[a-z]+|^[a-z]+')
                if not pattern.match(svc_name):
                   raise Exception("The deploy model of sheet's server name is Wrong!")
                
                if not re.match(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$', ip_addr):
                   raise Exception("The deploy model of sheet's ip addr is Wrong!")

                model_list.append(dict(zip(self.title, row), ))
            
            return model_list

    def get_business(self):
        """
        解析各业务线资源配置
        return:
        """
        merge_list = []
        sheet2 = self.workbook.sheet_by_index(1)
        sheet2_is_load = self.workbook.sheet_loaded(sheet_name_or_index=1)
        if not sheet2_is_load:
            logger.error(f"{sheet2} in {self.workbook}'s is load failed!")
        for (row_start, row_end, col_start, col_end) in sheet2.merged_cells:
            merge_list.append(sheet2.cell_value(rowx=row_start, colx=col_start))

        logger.info(f"sorted merge list: {sorted(merge_list)}")

        business_list = []
        for business in sorted(merge_list)[1:]:
            bus = {}
            if business == "RCX":
                bus["name"] = business
                bus["sort"] = 1
                bus["description"] = "RCX业务线"
            elif business == "RTC":
                bus["name"] = business
                bus["sort"] = 2
                bus["description"] = "RTC业务线"
            business_list.append(bus)
        logger.info(f"business info: {business_list}")
        return business_list

    @property
    def get_all_global_vars(self):
        """
        获取所有的全局变量
        :return:
        """
        try:
            sheet2 = self.workbook.sheet_by_index(1)
            if not self.workbook.sheet_loaded(sheet_name_or_index=1):
                logger.error(f"{sheet2} in {self.workbook}'s is load failed!")
            n, global_list = 0, list()
            for row in sheet2.get_rows():
                if n == 0:
                    n += 1
                    continue
                if "text" in str(row[2]):
                    self.business = str(row[2]).split(":")[1]
                
                temp_dict = dict()
                if str(row[0]).split(":")[1].replace("'", '') == "RTC_CLUSTER_ID":
                    logger.info(f"RTC_CLUSTER_ID: {row}")
                    v = str(str(row[1]).split(":", 1)[1]).replace("'", '')
                else:
                    v = str(str(row[1]).split(":")[1]).replace("'", '')
                temp_dict["key"] = str(str(row[0]).split(":")[1]).replace("'", '')
                temp_dict["value"] = int(round(float(v))) if self._isfloat_str(v) else str(v)
                temp_dict["isBase"] = True
                temp_dict["business"] = str(self.business).lower().replace("'", '')
                temp_dict["comment"] = str(str(row[3]).split(":")[1]).replace("'", '')

                global_list.append(temp_dict)

            config_list = global_list.copy()

            for item in config_list:
                if item["key"] == "'BASE_DIR'":
                    rtc_base_dir_dict = item.copy()
                    rtc_base_dir_dict["business"] = "rtc"
                    global_list.append(rtc_base_dir_dict)

            return global_list
        except Exception as e:
            logger.error(f"Get all global vars fo sheet's content failed!")

    def get_service(self):
        """
        解析各服务信息
        :return:
        """
        service_list = []
        for key, val in self.get_business().items():
            for item in val:
                temp_dict = {}
                temp_dict["name"] = item.get("service", None)
                temp_dict["business"] = item.get("business", None)
                service_list.append(temp_dict)

        return service_list

    @property
    def get_excel_dict(self):
        self._exce_dict = dict()
        self._exce_dict["resource"] = self.resource_sheet()
        self._exce_dict.update(self.business_sheet())
        return self._exce_dict

    def _float_to_num(self, row):
        row_list = list()
        for item in row:
            if not isinstance(item, str):
                row_list.append(int(item))
            else:
                row_list.append(item.strip())
        return row_list

    def _isfloat_str(self, str_number):
        try:
            float(str_number)
            return True
        except Exception as e:
            return False


if __name__ == '__main__':
    # ReadExcel().get_parse_business()
    global_list = ReadExcel().get_all_global_vars

    import json

    print(json.dumps(global_list, indent=4, ensure_ascii=False))

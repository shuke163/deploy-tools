#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: v2.py 
@time: 2020/03/20 20:38
@contact: shu_ke163@163.com
@software:  Door
"""

# from xlsxwriter import Workbook

players = [{'dailyWinners': 3, 'dailyFree': 2, 'user': 'Player1', 'bank': 0.06},
           {'dailyWinners': 3, 'dailyFree': 2, 'user': 'Player2', 'bank': 4.0},
           {'dailyWinners': 1, 'dailyFree': 2, 'user': 'Player3', 'bank': 3.1},
           {'dailyWinners': 3, 'dailyFree': 2, 'user': 'Player4', 'bank': 0.32}]

ordered_list = ["user", "dailyWinners", "dailyFree",
                "bank"]  # list object calls by index but dict object calls items randomly

wb = Workbook("New File.xlsx")
ws = wb.add_worksheet("New Sheet")  # or leave it blank, default name is "Sheet 1"

first_row = 0
for header in ordered_list:
    col = ordered_list.index(header)  # we are keeping order.
    ws.write(first_row, col, header)  # we have written first row which is the header of worksheet also.

row = 1
for player in players:
    for _key, _value in player.items():
        col = ordered_list.index(_key)
        ws.write(row, col, _value)
    row += 1  # enter the next row
wb.close()

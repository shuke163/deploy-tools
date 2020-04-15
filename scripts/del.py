#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author: your name
@Date: 2020-04-13 21:30:40
@LastEditTime: 2020-04-13 21:31:00
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /deploy-backend/scripts/del.py
'''

import os
import shutil

def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for dir in ds:
#            os.removedirs(os.path.join(root, dir))
            shutil.rmtree(os.path.join(root, dir))
            yield dir

def main():
    base = './'
    for i in findAllFile(base):
        print(i)


if __name__ == '__main__':
    main()
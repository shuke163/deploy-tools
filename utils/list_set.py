#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: shuke
@file: list_set.py 
@time: 2020/03/17 09:34
@contact: shu_ke163@163.com
@software:  Door
"""

from itertools import groupby
from operator import itemgetter

import pandas as pd


def distinct(items):
    questions = map(itemgetter('port'), items)
    df = pd.DataFrame({
        'items': items,
        'port': questions
    })
    return df.drop_duplicates(['port'])['items'].tolist()


def distinct2(items):
    exist_questions = set()
    result = []
    for item in items:
        question = item['question']
        if question not in exist_questions:
            exist_questions.add(question)
            result.append(item)
    return result


def distinct3(items):
    key = itemgetter('question')
    items = sorted(items, key=key)
    return [next(v) for _, v in groupby(items, key=key)]


def distinct4(items):
    from itertools import compress
    mask = (~pd.Series(map(itemgetter('port'), items)).duplicated()).tolist()
    return list(compress(items, mask))


if __name__ == '__main__':
    data = [
        {'question': 'a', 'ans': 'b'},
        {'question': 'b', 'ans': 'd'},
        {'question': 'a', 'ans': 'p'},
        {'question': 'b', 'ans': 'e'}
    ]

    data1 = [{'port': 8082, 'protocol': 'tcp'}, {'port': 8081, 'protocol': 'tcp'}, {'port': 8086, 'protocol': 'tcp'},
             {'port': 8043, 'protocol': 'tcp'}, {'port': 8085, 'protocol': 'wss'}, {'port': 8070, 'protocol': 'tcp'},
             {'port': 8043, 'protocol': 'tcp'}, {'port': 8085, 'protocol': 'wss'}, {'port': 8070, 'protocol': 'tcp'}]

    print(distinct(data1))

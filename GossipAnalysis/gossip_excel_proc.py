# !/usr/bin/env python3

import os
import xlrd
import json

datadir = '/Users/higgs/beast/doc/dict'
corp_file = os.path.join(datadir, '公司字典v1.2更新20180828.xlsx')

'''
公司字典v1.2更新20180828.xlsx:
    <class 'list'>: [text:'公司类型', text:'简称', text:'公司名', text:'英文名', text:'所属行业', text:'关键词', text:'创建时间', text:'更新时间', text:'备注']
'''

def read_execl(infile):
    workbook = xlrd.open_workbook(corp_file)
    sheets = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(sheets[0])
    corps = []
    for i in range(1, worksheet.nrows):
        dict = {}
        row = worksheet.row(i)
        dict['fullname'] = row[2].value
        dict['englishname'] = row[3].value
        dict['abbreviation'] = row[1].value
        dict['others'] = row[5].value.split('、')
        corps.append(dict)
    outdir = './dataset'
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, './corps_dict.txt')
    with open(outfile, 'w') as f:
        json.dump(corps, f)
    print('hello world!')


if __name__ == '__main__':
    read_execl(corp_file)
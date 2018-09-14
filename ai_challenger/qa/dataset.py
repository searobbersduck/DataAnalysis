# !/usr/bin/env python3
import os
import argparse
import sys
from glob import glob
import json
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.font_manager import FontProperties

def getChineseFont():
    return FontProperties(fname='/System/Library/Fonts/PingFang.ttc',size=15)

# plt.rcParams['font.sans-serif'] = ['SimHei'] # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号

def parse_args():
    parser = argparse.ArgumentParser(description='qa dataset')
    parser.add_argument('--datadir', default=None)
    return parser.parse_args()

args = parse_args()

data_dir = '/Users/higgs/beast/code/kaggle/DataAnalysis/ai_challenger/qa/dataset/ai_challenger_oqmrc_trainingset_20180816'
train_file = os.path.join(data_dir, 'ai_challenger_oqmrc_trainingset.json')
train_outfile = os.path.join(data_dir, 'qa_train.txt')

def out_train_file(infile, outfile):
    sents = []
    with open(infile, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if line is None or line == '':
                continue
            line = line.strip()
            if line is None or line == '':
                continue
            train_json = json.loads(line)
            url = train_json['url']
            alternatives = train_json['alternatives']
            passage = train_json['passage']
            query_id = train_json['query_id']
            answer = train_json['answer']
            query = train_json['query']
            alter_ss = alternatives.split('|')
            sents.append(query)
            sents.append(passage)
            if len(alter_ss) != 3:
                print(alternatives)
            else:
                for s in alter_ss:
                    sents.append(s)
            # print(line)
    with open(outfile, 'w', encoding='utf8') as f:
        sents_txt = '\n'.join(sents)
        f.write(sents_txt)
    print('hello world!')

'''
检查数据集：
1. 训练集合中是否，所有的问题的答案选项都是三个？
2. 问题的最大长度
3. 段落的最大长度
4. 数据集的长度

数据集预处理：
1. 生成字典/词向量
2. 分成训练集和验证集
'''

def stat_train_dataset(infile):
    json_qas = []
    with open(infile, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if line is None or line == '':
                continue
            json_qa = json.loads(line)
            json_qas.append(json_qa)
    passage_len_list = list(map(lambda x : min(500, len(x['passage'])), json_qas))
    passage_len_max = np.max(passage_len_list)
    query_len_list = list(map(lambda x: min(100, len(x['query'])), json_qas))
    query_len_max = np.max(query_len_list)
    print(u'问答总数: ', len(passage_len_list))
    print(u'段落的最大长度: ', passage_len_max)
    print(u'问题的最大长度: ', query_len_max)
    plt.figure(figsize=(20, 50))
    plt.subplot(211)
    plt.hist(np.array(passage_len_list), bins=40, normed=0, facecolor="blue", edgecolor="black", alpha=0.7)
    plt.xlabel(u'字数', fontproperties=getChineseFont())
    plt.ylabel(u'频率', fontproperties=getChineseFont())
    plt.title(u'段落字数分布直方图', fontproperties=getChineseFont())
    plt.subplot(212)
    plt.hist(np.array(query_len_list), bins=40, normed=0, facecolor="blue", edgecolor="black", alpha=0.7)
    plt.xlabel(u'字数', fontproperties=getChineseFont())
    plt.ylabel(u'频率', fontproperties=getChineseFont())
    plt.title(u'问题字数分布直方图', fontproperties=getChineseFont())
    plt.show()
    print('hello world')

if __name__ == '__main__':
    # out_train_file(train_file, train_outfile)
    stat_train_dataset(train_file)

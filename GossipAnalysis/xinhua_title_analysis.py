# !/usr/bin/env python3

import os
from glob import glob
import json
import sys
import multiprocessing
import jieba

xinhua_dataset = '/Users/higgs/beast/code/work/Duck_QA/xinhua_star/xinhua_data'
xinhua_dataset = '/Users/higgs/beast/code/work/Duck_QA/xinhua_star/xinhua_data_json'
xinhua_file_prefix = os.path.join(xinhua_dataset, 'file_*')

raw_title_file = './dataset/xinhua_titles.txt'
raw_title_seg_file = './dataset/xinhua_titles_seg.txt'
corp_dict_file = './dataset/corps_dict.txt'
corp_list_file = './dataset/corps_list.txt'
out_gossip_title_file = './dataset/xinhua_gossip_titles.txt'
out_gossip_title_boundary_file = './dataset/xinhua_gossip_boundary_titles.txt'
out_gossip_title_delete_xinhua_file = './dataset/xinhua_gossip_titles_delete_xinhua.txt'
out_gossip_title_delete_xinhua_bd_file = './dataset/xinhua_gossip_titles_bd_delete_xinhua.txt'

'''
1. 提取从新华网抓取的文章的标题
2. 按照公司名来匹配文章标题
'''

#1.
def extract_xinhua_title(infile_prefix):
    infile_list = glob(xinhua_file_prefix)
    titles = []
    for infile in infile_list:
        with open(infile, 'r') as f:
           article_json = json.load(f)
           for art in article_json:
               titles.append(art['title'])
    outdir = './dataset'
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, 'xinhua_titles.txt')
    with open(outfile, 'w', encoding='utf8') as f:
        outtxt = '\n'.join(titles)
        f.write(outtxt)


#2.
def extract_xinhua_title_by_corpname(raw_title_file, corp_dict_file):
    corps_all = []
    with open(corp_dict_file, 'r') as f:
        corps = json.load(f)
        for corp in corps:
            corps_all.append(corp['fullname'])
            corps_all.append(corp['englishname'])
            corps_all.append(corp['abbreviation'])
            corps_all += corp['others']
    while '' in corps_all:
        corps_all.remove('')
    gossip_titles = []
    with open(raw_title_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if line is None or line == '':
                continue
            for corp in corps_all:
                if corp in line:
                    gossip_titles.append('{}\t{}'.format(corp,line))
                    break
    with open(out_gossip_title_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(gossip_titles))
    print('extract_xinhua_title_by_corpname finished!')


def hit_word(indict_list, in_sent_list, outdict, process_id):
    print('====> process {} begin!'.format(process_id))
    list = []
    icnt = 0
    for sent in in_sent_list:
        icnt += 1
        if (icnt%1000 == 0):
            print('====> process {}:\t{} sentences has been processed!'.format(process_id, icnt))
        for word in indict_list:
            if word in sent:
                list.append('{}\t{}'.format(word, sent))
                break
    outdict[process_id] = list
    print('====> process {} finished!'.format(process_id))

def extract_xinhua_title_by_corpname_mt(raw_title_file, corp_dict_file):
    corps_all = []
    with open(corp_dict_file, 'r') as f:
        corps = json.load(f)
        for corp in corps:
            corps_all.append(corp['fullname'])
            corps_all.append(corp['englishname'])
            corps_all.append(corp['abbreviation'])
            corps_all += corp['others']
    while '' in corps_all:
        corps_all.remove('')
    gossip_titles = []
    raw_titles = []
    with open(raw_title_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if line is None or line == '':
                continue
            raw_titles.append(line)
    process_num = 12
    n_block = (len(raw_titles) + process_num - 1) // process_num
    raw_titles_block = []
    for i in range(n_block):
        start_i = i * n_block
        end_i = min((i+1)*n_block, len(raw_titles)-1)
        raw_titles_block.append(raw_titles[start_i:end_i])
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []
    for i in range(process_num):
        proc = multiprocessing.Process(target=hit_word,
                                       args=(corps_all, raw_titles_block[i], return_dict, i))
        processes.append(proc)
    for i in processes:
        i.start()
    for i in processes:
        i.join()
    for key in return_dict.keys():
        gossip_titles += return_dict[key]
    with open(out_gossip_title_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(gossip_titles))
    print('extract_xinhua_title_by_corpname finished!')

def hit_word_boundary(indict_list, in_sent_list, outdict, process_id):
    print('====> process {} begin!'.format(process_id))
    list = []
    icnt = 0
    for sent in in_sent_list:
        ss_sent = sent.split('\t')
        sent_0 = ss_sent[0]
        icnt += 1
        if (icnt%1000 == 0):
            print('====> process {}:\t{} sentences has been processed!'.format(process_id, icnt))
        for word in indict_list:
            if word in sent_0:
                b_i = 0
                e_i = 0
                for index, subword in enumerate(ss_sent[1:], start=1):
                    if word.startswith(subword):
                        b_i = index
                    if word.endswith(subword):
                        e_i = index
                word_suspect = ''.join(ss_sent[b_i:e_i+1])
                if word_suspect == word:
                    list.append('{}\t{}'.format(word, sent))
                    break
    outdict[process_id] = list
    print('====> process {} finished!'.format(process_id))


def extract_xinhua_title_by_corpname_mt_boundary(raw_title_file, corp_list_file):
    corps_all = []
    with open(corp_list_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if line is None or line == '':
                continue
            corps_all.append(line)
    gossip_titles = []
    raw_titles = []
    with open(raw_title_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if line is None or line == '':
                continue
            raw_titles.append(line)
    process_num = 12
    n_block = (len(raw_titles) + process_num - 1) // process_num
    raw_titles_block = []
    for i in range(n_block):
        start_i = i * n_block
        end_i = min((i+1)*n_block, len(raw_titles)-1)
        raw_titles_block.append(raw_titles[start_i:end_i])
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []
    for i in range(process_num):
        proc = multiprocessing.Process(target=hit_word_boundary,
                                       args=(corps_all, raw_titles_block[i], return_dict, i))
        processes.append(proc)
    for i in processes:
        i.start()
    for i in processes:
        i.join()
    for key in return_dict.keys():
        gossip_titles += return_dict[key]
    with open(out_gossip_title_boundary_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(gossip_titles))
    print('extract_xinhua_title_by_corpname finished!')

def delete_xinhua_keyword(infile, outfile):
    list = []
    with open(infile, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if line is None or line == '':
                continue
            if '新华网' not in line:
                list.append(line)
    with open(outfile, 'w', encoding='utf8') as f:
        f.write('\n'.join(list))

def write_corpname_to_file(corp_dict_file, corp_list_file):
    corps_all = []
    with open(corp_dict_file, 'r') as f:
        corps = json.load(f)
        for corp in corps:
            corps_all.append(corp['fullname'])
            corps_all.append(corp['englishname'])
            corps_all.append(corp['abbreviation'])
            corps_all += corp['others']
    while '' in corps_all:
        corps_all.remove('')
    corps_all = list(set(corps_all))
    with open(corp_list_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(corps_all))

def generate_xinhua_titles(raw_title_file, raw_title_seg_file):
    seg_list = []
    with open(raw_title_file, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if line is None or line == '':
                continue
            line_seg = list(jieba.cut(line))
            line_seg = '\t'.join(line_seg)
            seg_list.append('{}\t{}'.format(line, line_seg))
    with open(raw_title_seg_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(seg_list))

if __name__ == '__main__':
    # extract_xinhua_title(xinhua_file_prefix)
    # extract_xinhua_title_by_corpname(raw_title_file, corp_dict_file)
    # extract_xinhua_title_by_corpname_mt(raw_title_file, corp_dict_file)
    extract_xinhua_title_by_corpname_mt_boundary(raw_title_seg_file, corp_list_file)
    delete_xinhua_keyword(out_gossip_title_boundary_file, out_gossip_title_delete_xinhua_bd_file)
    # write_corpname_to_file(corp_dict_file, corp_list_file)
    # generate_xinhua_titles(raw_title_file, raw_title_seg_file)
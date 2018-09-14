# !/usr/bin/env python3

import os
import sys
import json

infile = './dataset/maimai_sample_5w.txt'


'''
1. 统计likes数目，画出分布直方图
2. 发布者统计
3. text的词频统计
4. 每一项中的keys：dict_keys(['is_freeze', 'username', 'id', 'likes', 'text', 'search_qs', 'search_order', 'avatar', 'crtime_string', 'author', 'crtime', 'total_cnt', 'summary'])
'''

with open(infile, 'r', encoding='utf8') as f:
    gossip_set = []
    gossip_set_likes = []
    gossip_set_authors = []
    gossip_set_text = []
    for line in f.readlines():
        line = line.strip()
        if line is None or line == '':
            continue
        gossip_item = json.loads(line)
        gossip_set_likes.append(int(gossip_item['likes']))
        gossip_set_authors.append(gossip_item['username'])
        gossip_set_text.append(gossip_item['text'])


# if __name__ == '__main__':

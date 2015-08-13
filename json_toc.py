#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

url = "http://swim.reverland.org"

with open('./rebuild.sh') as f:
    lines = f.readlines()[2:]

t = [x.strip('# \n') for x in lines[-2::-2]]
dic = [(x.split('|')[0].decode('utf-8'), x.split('|')[1]) for x in t]
new_dic = {}

for i in range(len(dic)):
    new_dic[i] = {
        "url": url + '/' + dic[i][0] + '.html',
        "date": dic[i][1]
    }

data = json.dumps(new_dic)

with open('./html/toc.json', 'wb') as f:
    f.write(data)

import json
import os
from pathlib import Path

with open('data.txt', 'r') as datafile:
    data = json.load(datafile)

olddata = data[0]
# print(olddata)
newdata = {}


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


filedir = Path('tmpdata', olddata['id'])
# print(filedir)
for key, value in olddata['fields'].items():
    # print('key: {}; findkeys: {}'.format(key, list(findkeys(value, 'url'))))
    urls = list(findkeys(value, 'url'))
    if urls:
        paths = os.listdir(filedir)
        newdata[key] = [paths]
    else:
        newdata[key] = value


print(newdata)

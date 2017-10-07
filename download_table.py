import airtable
from pathlib import Path
import os
import json
import requests
import base64

outfilename = os.environ['OUTFILE']
outpath = os.environ['OUTPATH']
outfile = Path(outpath, outfilename)

table = airtable.Airtable(base_key=os.environ['ATDB'],
                          api_key=os.environ['ATKEY'],
                          table_name=os.environ['TABLE'])

table_data = table.get_all()

# assert len(table_data) == 501

# print(table_data[0:2])
with open('data.txt', 'w') as datafile:
    json.dump(table_data, datafile)


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


basepath = Path(outpath)
newrecords = []
keys = []

for record in table_data:
    newdata = {}
    for key, value in record['fields'].items():
        if key not in keys:
            keys.append(key)
        if list(findkeys(value, 'url')):
            filedata = []
            for item in value:
                data = requests.get(item['url'])
                encoded = base64.b64encode(data.content)
                fileinfo = {
                    'filename': item['filename'],
                    'data': encoded.decode('utf-8')
                }
                filedata.append(fileinfo)
            newdata[key] = filedata
        else:
            newdata[key] = value
    newrecords.append(newdata)


with open(outfile, 'w') as datafile:
    json.dump(newrecords, datafile, indent=2)

import airtable
from pathlib import Path
import os
import json
import requests
import base64


table = airtable.Airtable(base_key=os.environ['ATDB'],
                          api_key=os.environ['ATKEY'],
                          table_name='giant_table')

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


basepath = Path('tmpdata')
newrecords = []
keys = []

for record in table_data:
    newdata = {}
    for key, value in record['fields'].items():
        if key not in keys:
            kes.append(key)
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

with open('everything.json', 'w') as datafile:
    json.dump(newrecords, datafile, indent=2)
# print(json.dumps(newrecords, indent=2))
# for item in newrecords:
#     for rec in item['Attachments']:
#         print(rec['filename'])
#         print(base64.b64decode(rec['data']))
#
# for record in table_data[0:2]:
#     # print('recid: {}'.format(record['id']))
#     for num, item in enumerate(findkeys(record, 'url')):
#         data = requests.get(item)
#         filespath = Path(basepath, str(record['id']))
#         os.makedirs(filespath, exist_ok=True)
#         with open(Path(filespath, 'attach' + str(num)), 'wb') as datafile:
#             datafile.write(data.content)

import json
import os
import requests
import s3interface
import airtable
import boto3
from pathlib import Path
import base64


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


BUCKET = os.environ['UPBUCKET']
table = airtable.Airtable(base_key=os.environ['ATDBNEW'],
                          api_key=os.environ['ATKEY'],
                          table_name='giant_table')

s3 = boto3.resource('s3')
s3client = boto3.client('s3')

with open('everything.json', 'r') as datafile:
    data = json.load(datafile)

assert len(data) == 501
newrecords = []
for record in data[0:3]:
    newdata = {}
    print(record)
    for key, value in record.items():
        if list(findkeys(value, 'filename')):
            urls = []
            for item in value:
                filename = 'atrestoretest/' + item['filename']
                # print(filename)
                # print(base64.b64decode(item['data']))
                upload = s3.Object(BUCKET, filename)
                upload.put(Body=base64.b64decode(item['data']))
                upload.put(Body=base64.b64decode(item['data']))
                upload.put(Body=base64.b64decode(item['data']))
                url = s3client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': BUCKET,
                        'Key': filename
                    }
                )
                urls.append({'url': url})
            newdata[key] = urls
        else:
            newdata[key] = value
    newrecords.append(newdata)

print(json.dumps(newrecords, indent=2))

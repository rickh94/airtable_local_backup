import json
import lzma
import os
import requests
import s3interface
import airtable
import boto3
from pathlib import Path
import base64
import hashlib
from airtable_local_backup import exceptions


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


INFILEPATH = Path(os.environ['INPATH'], os.environ['INFILE'])
BUCKET = os.environ['UPBUCKET']
table = airtable.Airtable(base_key=os.environ['ATDBNEW'],
                          api_key=os.environ['ATKEY'],
                          table_name=os.environ['TABLE'])

s3 = boto3.resource('s3')
s3client = boto3.client('s3')

with open(INFILEPATH, 'r') as datafile:
    data = json.load(datafile)


def read_data(table_data):
    """
    Reads table data from input stream and yields records for insertion into
    airtable.
    """
    for record in data:
        newdata = {}
        # print(record)
        for key, value in record.items():
            if list(findkeys(value, 'filename')):
                urls = []
                for item in value:
                    filename = 'atrestoretest/' + item['filename']
                    upload = s3.Object(BUCKET, filename)
                    filedata = base64.b64decode(item['data'])
                    if item['compressed']:
                        body = lzma.decompress(filedata)
                    else:
                        body = filedata
                    bodyhash = hashlib.md5(filedata).hexdigest()
                    if not bodyhash == item['md5hash']:
                        raise exceptions.DataCorruptionError(
                            'file: {} failed the data integrity check, '
                            'and may be corrupted.')
                    upload.put(Body=body)
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

        yield newdata
    # table.insert(newdata)

# print(json.dumps(newrecords, indent=2))

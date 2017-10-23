import os
import json
import datetime
from fs_s3fs import S3FS
from airtable import Airtable
from airtable_local_backup import restore


base = os.environ['ATDB']
table_name = os.environ['TABLE']
dokey = os.environ['DOKEY']
dosecret = os.environ['DOSECRET']
endpoint_url = os.environ['URL']
bucket = os.environ['BUCKET']
prefix = 'testrestore-{}/'.format(datetime.datetime.now())

table = Airtable(base_key=base, table_name=table_name)
space = S3FS(bucket, endpoint_url=endpoint_url, aws_access_key_id=dokey,
             aws_secret_access_key=dosecret)

with open('tests/lots_of_fields.json', 'r') as jsonfile:
    tabledata = json.load(jsonfile)

records = restore.prepare_records(tabledata, s3fs=space, check_integrity=True,
                                  prefix=prefix)

for rec in records:
    table.insert(rec)

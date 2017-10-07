from airtable.airtable import Airtable
import s3interface
from pathlib import Path
import os
from uuid import uuid4
from time import sleep

db = Airtable(api_key=os.environ['ATKEY'],
              base_id=os.environ['ATDB'])
basepath = Path('/home', 'rick', 'tmp', 'garbagefiles')

for i in range(0, 501):
    sleep(0.2)
    filepath = Path(basepath, 'file' + str(i) + '.txt')
    url = s3interface.make_url(filename=str(filepath),
                               bucket='ricksencryptedbucket')
    attach = [{'url': url}]
    data = {'Number': i, 'UUID': str(uuid4()), 'Attachments': attach}
    db.create('giant_table', data)

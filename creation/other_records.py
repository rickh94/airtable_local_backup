from airtable import Airtable
import s3interface
from pathlib import Path
import os
from uuid import uuid4
from time import sleep
import random
from random_words import RandomWords

table = Airtable(api_key=os.environ['ATKEY'],
                 base_key=os.environ['ATDB'],
                 table_name='Sheet Music')
basepath = Path('..', 'big-binaries')


for pdf in os.listdir(basepath)[0:100]:
    filepath = Path(basepath, pdf)
    url = s3interface.make_url(filename=str(filepath),
                               bucket='ricksencryptedbucket')
    attach = [{'url': url}]
    rw = RandomWords()
    UUID = str(uuid4())
    words = ' '.join(rw.random_words(count=10))
    check = bool(random.randrange(0, 2))
    randomdata = {
        'Name': pdf,
        'Notes': words,
        'Attachments': attach,
    }
    # print(randomdata)
    table.insert(randomdata)

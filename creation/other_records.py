from airtable.airtable import Airtable
import s3interface
from pathlib import Path
import os
from uuid import uuid4
from time import sleep
import names
import random
from random_words import RandomWords

db = Airtable(api_key=os.environ['ATKEY'],
              base_id=os.environ['ATDB'])
basepath = Path('/home', 'rick', 'tmp', 'garbagefiles')

for i in range(0, 200):
    sleep(0.1)
    filepath1 = Path(basepath, 'file' + str(i) + '.txt')
    url1 = s3interface.make_url(filename=str(filepath1),
                                bucket='ricksencryptedbucket')
    filepath2 = Path(basepath, 'file' + str((i + 201)) + '.txt')
    url2 = s3interface.make_url(filename=str(filepath2),
                                bucket='ricksencryptedbucket')
    attach = [{'url': url1}, {'url': url2}]
    rw = RandomWords()
    words = ' '.join(rw.random_words(count=10))
    check = bool(random.randrange(0, 2))
    randomdata = {
        'ID': i,
        'Notes': words,
        'Attachments': attach,
        'Check': check
    }
    # print(randomdata)
    db.create('Random Data', randomdata)

    fname = names.get_first_name()
    lname = names.get_last_name()
    email = fname[0].lower() + lname.lower() + '@example.com'
    a = random.randrange(0, 999)
    b = random.randrange(0, 999)
    c = random.randrange(0, 9999)
    phone = '{:03d}-{:03d}-{:04d}'.format(a, b, c)
    contactdata = {
        'Last Name': lname,
        'First Name': fname,
        'Email Address': email,
        'Phone Number': phone
    }
    # print(contactdata)
    db.create('Contacts', contactdata)

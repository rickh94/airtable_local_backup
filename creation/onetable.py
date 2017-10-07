from airtable import Airtable
import os


table = Airtable(api_key=os.environ['ATKEY'],
                 base_key=os.environ['ATDB'],
                 table_name='table2')
table.insert({'Name': 'hi'})

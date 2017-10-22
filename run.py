import os
import json
import tempfile
import pickle
from tqdm import tqdm
from airtable_local_backup import download
from airtable import Airtable

BASE = os.environ['ATDB']
TABLE = os.environ['TABLE']


def main():
    table = Airtable(base_key=BASE, table_name=TABLE)
    data = table.get_all()
    # with open('tests/lots_of_fields_raw.pickle', 'wb') as datafile:
    #     pickle.dump(data, datafile)

    downloadtable = download.DownloadTable(base_key=BASE, table_name=TABLE)
    all_data = []
    for item in downloadtable.download_table():
        all_data.append(item)

    # all_data = list(downloadtable.download_table())
    # with open('tests/lots_of_fields_data.pickle', 'wb') as datafile:
    #     pickle.dump(all_data, datafile)

    with open('/tmp/test_lots_of_fields.json', 'w') as jsonfile:
        json.dump(all_data, jsonfile, indent=2)
    # print(json.dumps(list(all_data), indent=2))
    # for item in all_data:
    #     tmpdata.write(

    # print(json.dumps(all_data,
    #                  # indent=2
    #                  )
    #       )


if __name__ == '__main__':
    main()

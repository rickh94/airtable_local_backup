import os
import json
import tempfile
import pickle
from airtable_local_backup import download
from airtable import Airtable

BASE = os.environ['ATDB']
TABLE = os.environ['TABLE']


def main():
    table = Airtable(base_key=BASE, table_name=TABLE)
    data = table.get_all()
    with open('tests/lots_of_fields_raw.pickle', 'wb') as datafile:
        pickle.dump(data, datafile)

    all_data = list(download.DownloadTable(base_key=BASE, table_name=TABLE,
                                           progress=False))
    with open('tests/lots_of_fields_data.pickle', 'wb') as datafile:
        pickle.dump(all_data, datafile)

    with open('tests/lots_of_fields.json', 'w') as jsonfile:
        json.dump(all_data, jsonfile)
    # print(json.dumps(list(all_data), indent=2))
    # for item in all_data:
    #     tmpdata.write(

    # print(json.dumps(all_data,
    #                  # indent=2
    #                  )
    #       )


if __name__ == '__main__':
    main()

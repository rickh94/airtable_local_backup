import os
import json
import tempfile
import pickle
from airtable_local_backup import download

BASE = os.environ['ATDB']
TABLE = os.environ['TABLE']


def main():
    all_data = download.DownloadTable(base_key=BASE, table_name=TABLE,
                                      progress=True)
    print(json.dumps(list(all_data), indent=2))
    # for item in all_data:
    #     tmpdata.write(

    # print(json.dumps(all_data,
    #                  # indent=2
    #                  )
    #       )


if __name__ == '__main__':
    main()

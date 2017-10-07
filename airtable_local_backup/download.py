import airtable
from pathlib import Path
import os
import json
import requests
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


# TODO: add option flags for: compression
# TODO: add optional dict of keys for recording the fields
def download_table(base_key, table_name, api_key=None):
    """
    Downloads all data from a table including atachments.

    Arguments:
        base_key: base id from airtable api url (starts 'app')
        table_name: the table name to download
        api_key: the airtable api key. If an environment variable
            'AIRTABLE_API_KEY' is set this is not required.

    Returns:
        A json-serializable dict of all data that can be written to a file.
    """
    table = airtable.Airtable(base_key=base_key,
                              api_key=api_key,
                              table_name=table_name)
    table_data = table.get_all()
    newrecords = []
    for record in table_data:
        newdata = {}
        for key, value in record['fields'].items():
            if key not in keys:
                keys.append(key)
            if list(findkeys(value, 'url')):
                filedata = []
                for item in value:
                    data = requests.get(item['url'])
                    encoded = base64.b64encode(data.content)
                    fileinfo = {
                        'filename': item['filename'],
                        'data': encoded.decode('utf-8')
                    }
                    filedata.append(fileinfo)
                newdata[key] = filedata
            else:
                newdata[key] = value
        newrecords.append(newdata)

    return newrecords

    # with open(outfile, 'w') as datafile:
    #     json.dump(newrecords, datafile, indent=2)

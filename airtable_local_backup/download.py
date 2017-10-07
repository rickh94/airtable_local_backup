import base64
import airtable
import requests
import lzma


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


class DownloadTable(list):
    """
    Downloads all data from a table including atachments.

    Arguments:
        base_key: base id from airtable api url (starts 'app')
        table_name: the table name to download
        api_key: the airtable api key. If an environment variable
            'AIRTABLE_API_KEY' is set this is not required.

    Returns:
        A generator that will yield all the data in the table.
    """
    # TODO: add option flags for: compression
    # TODO: add optional dict of keys for recording the fields
    def __init__(self, base_key, table_name, api_key=None, progress=False,
                 compression=True):
        self.base_key = base_key
        self.table_name = table_name
        self.api_key = api_key
        self.downloaded = 0
        self.progress = progress
        self.compression = compression

    def __iter__(self):
        return self._download_table()

    def _download_table(self):
        table = airtable.Airtable(base_key=self.base_key,
                                  api_key=self.api_key,
                                  table_name=self.table_name)
        table_data = table.get_all()
        for record in table_data:
            # newrecords.append(extract_record(record))
            newdata = {}
            for key, value in record['fields'].items():
                # if key not in keys:
                #     keys.append(key)
                if list(findkeys(value, 'url')):
                    filedata = []
                    for item in value:
                        download = requests.get(item['url'])
                        if self.compression:
                            data = lzma.compress(download.content)
                        else:
                            data = download.content
                        encoded = base64.b64encode(data)
                        fileinfo = {
                            'filename': item['filename'],
                            'data': encoded.decode('utf-8'),
                            'compressed': self.compression,
                        }
                        filedata.append(fileinfo)
                    newdata[key] = filedata
                else:
                    newdata[key] = value
            self.downloaded += 1
            if self.progress:
                print('Downloaded: {}'.format(self.downloaded))
            yield newdata

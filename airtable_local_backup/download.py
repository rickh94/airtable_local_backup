"""Functions for downloading items from airtable."""
import base64
import lzma
from hashlib import md5
import airtable
import requests
from airtable_local_backup import common


# change this to inherit from the airtable.Airtable object
class DownloadTable(object):
    """
    Downloads all data from a table including atachments.

    :param base_key: base id from airtable api url (starts 'app')
    :param table_name: the table name to download
    :param api_key: the airtable api key. If an environment variable
            'AIRTABLE_API_KEY' is set this is not required.

    :param compression: whether to compress attachment data
    :param fields: Store the field
    :param discard_attach: if true, attachment data will not be downloaded, url
        and other info will be preservered
    """
    def __init__(self, base_key, table_name, api_key=None, progress=False,
                 compression=True, fields=dict(), discard_attach=False):
        self.base_key = base_key
        self.table_name = table_name
        self.api_key = api_key
        self.compression = compression
        self.fields = fields
        self.discard_attach = discard_attach

    def download(self):
        """
        Download the data in the table.

        :return: A generator that will download each item in the table as it is
              iterated based on the options configured.
        """
        table = airtable.Airtable(base_key=self.base_key,
                                  api_key=self.api_key,
                                  table_name=self.table_name)
        table_data = table.get_all()
        # possibly discretize loop into its own function
        for record in table_data:
            # newrecords.append(extract_record(record))
            newdata = {}
            for key, value in record['fields'].items():
                if key not in self.fields:
                    self.fields[key] = 'Unknown'
                if list(common._findkeys(value, 'url')) \
                        and not self.discard_attach:
                    filedata = []
                    for item in value:
                        fileinfo = _get_attach(item['filename'],
                                               item['url'],
                                               self.compression)
                        filedata.append(fileinfo)
                    newdata[key] = filedata
                else:
                    newdata[key] = value
            yield newdata


def _get_attach(filename, url, compression):
    download = requests.get(url)
    filehash = md5(download.content).hexdigest()
    if compression:
        data = lzma.compress(download.content)
    else:
        data = download.content
    encoded = base64.b64encode(data)
    return {
        'filename': filename,
        'data': encoded.decode('utf-8'),
        'compressed': compression,
        'md5hash': str(filehash)
    }

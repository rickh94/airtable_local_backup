import os

from airtable import Airtable
import requests
import pytest
import fs

from airtable_local_backup import file_io
from airtable_local_backup import download


def rettrue(*args):
    return True


def test_make_file_name():
    assert file_io._make_file_name('table', 'prefix', 'suffix') ==\
        'prefixtablesuffix.json'
    assert file_io._make_file_name('table', '', '-thing') ==\
        'table-thing.json'
    assert file_io._make_file_name('table', 'prefix/', '') ==\
        'prefix/table.json'
    assert file_io._make_file_name('My-test table', 'prefix/', '-2') ==\
        'prefix/my_test_table-2.json'


def test_write_to_file(filedata, lots_of_fields_raw, monkeypatch, tmpdir):
    def get_attach_patched(url):
        class FakeDownload():
            def __init__(self, data):
                self.content = data.encode('utf-8')
        return FakeDownload(filedata[url])

    def get_table_data(*args):
        return lots_of_fields_raw
    monkeypatch.setattr(Airtable, 'validate_session', rettrue)
    monkeypatch.setattr(Airtable, 'get_all', get_table_data)
    monkeypatch.setattr(requests, 'get', get_attach_patched)
    monkeypatch.setenv('AIRTABLE_API_KEY', '')
    table = download.DownloadTable(base_key='app12345', api_key='key12345',
                                   table_name='lots of fields')
    test_tmpfs = fs.open_fs(str(tmpdir))
    file_io._write_to_file(table, tmpfs=test_tmpfs, prefix='prefix/',
                           suffix='-hi')
    assert 'lots_of_fields-hi.json' in os.listdir(tmpdir + '/prefix')
    with open(tmpdir + '/prefix/lots_of_fields-hi.json', 'r') as datafile:
        data = datafile.read()
        assert 'Name' in data
        assert 'Attachments' in data
        assert 'file1.txt' in data
        assert 'md5hash' in data
        assert 'compressed' in data
        assert 'file15.txt' in data

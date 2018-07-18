import os
from pathlib import Path

from airtable import Airtable
import requests
import pytest
import fs
from fs import tarfs
from fs.copy import copy_fs

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
    assert file_io._make_file_name('Things/Stuff', 'there/', 'now') ==\
        'there/things_stuffnow.json'


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
    file_io.write_to_file(table, tmpfs=test_tmpfs, prefix='prefix/',
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


@pytest.fixture
def tmp_fs(tmpdir_factory, filedata):
    tmpdir = tmpdir_factory.mktemp('files_in')
    test_tmpfs = fs.open_fs(str(tmpdir))
    for key, value in filedata.items():
        with test_tmpfs.open(key, 'w') as tmpfile:
            tmpfile.write(value)
    return test_tmpfs


def test_join_files(tmpdir, filedata, tmp_fs, monkeypatch):
    outfile = Path(tmpdir, 'testtar.tar.xz')
    test_outfs = tarfs.TarFS(str(outfile),
                             compression='xz', write=True)
    file_io.join_files(tmp_fs, test_outfs)
    test_readout = tarfs.TarFS(str(outfile))
    for key, value in filedata.items():
        assert key in test_readout.listdir('/')
        with test_readout.open(key, 'r') as outfile:
            assert value in outfile.read()
    test_readout.close()


@pytest.fixture
def tarfile(tmpdir_factory, filedata, tmp_fs):
    tardir = tmpdir_factory.mktemp('tar_fixture')
    path = Path(tardir, 'stuff.tar')
    tar_fs = tarfs.TarFS(str(path), write=True)
    copy_fs(tmp_fs, tar_fs)
    tar_fs.close()
    return path


def test_write_out_backup(tmpdir_factory, filedata, tarfile, tmp_fs):
    testdir1 = tmpdir_factory.mktemp('write_out_backup_1')
    testdir2 = tmpdir_factory.mktemp('write_out_backup_2')
    testdir3 = tmpdir_factory.mktemp('write_out_backup_3')
    testdir4 = tmpdir_factory.mktemp('write_out_backup_4')
    testdir5 = tmpdir_factory.mktemp('write_out_backup_5')
    back_fs1 = fs.open_fs(str(testdir1))
    back_fs2 = fs.open_fs(str(testdir2))
    back_fs3 = fs.open_fs(str(testdir3))
    back_fs4 = fs.open_fs(str(testdir4))
    back_fs5 = fs.open_fs(str(testdir5))
    file_io.write_out_backup([back_fs1, back_fs2],
                              filepath=tarfile)
    file_io.write_out_backup(back_fs3,
                              filesystem=tmp_fs, prefix='hi/')
    file_io.write_out_backup(back_fs4,
                              filesystem=tmp_fs, prefix='hi')
    file_io.write_out_backup(back_fs5,
                              filesystem=tmp_fs)
    assert 'stuff.tar' in back_fs1.listdir('/')
    assert 'stuff.tar' in back_fs2.listdir('/')
    back_fs1.close()
    back_fs2.close()
    tarout1 = tarfs.TarFS(str(testdir1) + '/stuff.tar')
    tarout2 = tarfs.TarFS(str(testdir2) + '/stuff.tar')
    for key, value in filedata.items():
        with tarout1.open(key) as testfile:
            assert value in testfile
        with tarout2.open(key) as testfile:
            assert value in testfile
        assert key in back_fs3.listdir('/hi')
        assert key in back_fs4.listdir('/hi')
        assert key in back_fs5.listdir('/')
        with back_fs3.open('hi/' + key) as testfile:
            assert value in testfile
        with back_fs4.open('hi/' + key) as testfile:
            assert value in testfile
        with back_fs5.open(key) as testfile:
            assert value in testfile

    with pytest.raises(AttributeError):
        file_io.write_out_backup(back_fs1)

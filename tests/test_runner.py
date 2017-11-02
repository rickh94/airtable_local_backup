import os
from pathlib import Path
from unittest import mock

from airtable import Airtable
from fs import open_fs
import pytest
import requests

from airtable_local_backup import runner
from airtable_local_backup.exceptions import ConfigurationError
from airtable_local_backup.file_io import _normalize

HERE = os.path.dirname(__file__)
DATA = Path(HERE, 'testdata')


@pytest.fixture
def testconf_yml():
    return os.path.abspath(Path(DATA, 'testconf.yml'))


@pytest.fixture
def badconf_yml():
    return os.path.abspath(Path(DATA, 'bad.yml'))


@pytest.fixture
def testrunner(testconf_yml, monkeypatch, lots_of_fields_raw,
                filedata):
    monkeypatch.setattr(Airtable, 'validate_session', rettrue)
    monkeypatch.setenv('AIRTABLE_API_KEY', 'key123456')

    def ret_data(*args):
        return lots_of_fields_raw

    def get_attach_patched(url):
        class FakeDownload():
            def __init__(self, data):
                self.content = data.encode('utf-8')
        return FakeDownload(filedata[url])

    monkeypatch.setattr(Airtable, 'get_all', ret_data)
    monkeypatch.setattr(requests, 'get', get_attach_patched)
    return runner.Runner(path=testconf_yml)

@pytest.fixture
def bad_testrunner(badconf_yml):
    return runner.Runner(path=badconf_yml)


@pytest.fixture
def table_names():
    return ['giant_table', 'Contacts', 'Random Data', 'Lots of fields']


def test_config(testrunner):
    assert testrunner.config['Base Name'] == 'TestDB'
    assert testrunner.config['Airtable Base Key'] == 'app123456'
    assert testrunner.config['Airtable API Key'] is None
    assert testrunner.config['Store As']['Type'] == 'tar'
    assert testrunner.config['Store As']['Compression'] == 'xz'
    assert testrunner.config['Backing Store']['Type'] == 'S3'
    assert testrunner.config['Backing Store']['Bucket'] == 'mybackupbucket'
    assert testrunner.config['Backing Store']['Prefix'] == 'backupfolder/'
    assert testrunner.config['Backing Store']['Date'] is True
    assert testrunner.config['Tables'][0]['Name'] == 'giant_table'
    assert testrunner.config['Tables'][1]['Fields']['Last Name'] ==\
        'Single line text'
    assert testrunner.config['Attachment Store']['Type'] == 'S3'
    assert testrunner.config['Attachment Store']['Bucket'] ==\
        'testairtableattachments'
    assert testrunner.config['Attachment Store']['Key ID'][0] == '$'


def test_create_backup_tables(testrunner, table_names, bad_testrunner):
    for table in testrunner._create_backup_tables():
        assert table.base_key == 'app123456'
        assert table.api_key is None
        assert table.compression is True
        assert table.discard_attach is False
        assert isinstance(table.fields, dict)
        assert table.table_name in table_names
        # remove the table because there should be only one of each
        table_names.remove(table.table_name)
    assert table_names == [], "All tables should have been removed"
    with pytest.raises(ConfigurationError):
        list(bad_testrunner._create_backup_tables())


def rettrue(*args):
    return True


def test_save_tables(testrunner, table_names):
    testrunner._save_tables()
    for table in table_names:
        name = _normalize(table)
        assert f'{name}.json' in testrunner.tmp.listdir('/')


def test_configure_backing_store(testrunner, monkeypatch, bad_testrunner):
    testfs1 = testrunner._configure_backing_store()
    assert testfs1._bucket_name == 'mybackupbucket'
    assert testfs1.aws_access_key_id is None
    assert testfs1.aws_secret_access_key is None
    assert testfs1.endpoint_url is None
    assert testfs1.strict is False
    testfs1.close()

    monkeypatch.setenv('DOKEY', 'testkeyid')
    monkeypatch.setenv('DOSECRET', 'testsecretkey')
    test2runner = runner.Runner(str(Path(DATA, 'testconf-2.yml')))
    testfs2 = test2runner._configure_backing_store()
    assert testfs2._bucket_name == 'testbackupspace'
    assert testfs2.aws_access_key_id == 'testkeyid'
    assert testfs2.aws_secret_access_key == 'testsecretkey'
    assert testfs2.endpoint_url == 'https://nyc3.digitaloceanspaces.com'
    assert testfs2.strict is False
    testfs2.close()

    test3runner = runner.Runner(str(Path(DATA, 'testconf-3.yml')))
    testfs3 = test3runner._configure_backing_store()
    assert testfs3.root_path == '/tmp/testbackupdir'
    testfs3.close()
    assert os.path.exists('/tmp/testbackupdir')
    assert os.path.isdir('/tmp/testbackupdir')

    with pytest.raises(ConfigurationError):
        bad_testrunner._configure_backing_store()


def test_package(testrunner, tmpdir, table_names):
    testfile = Path(tmpdir, 'testtar.tar')
    testrunner._save_tables()
    testrunner._package(str(testfile))
    testtar = open_fs(f"tar://{testfile}")
    for name in table_names:
        assert f"{_normalize(name)}.json" in testtar.listdir('/')


def test_backup(testrunner, bad_testrunner, tmpdir, monkeypatch):
    dirnumber = [0]
    def localfs(*args):
        name = f"backup{dirnumber[0]}"
        path = Path(tmpdir, name)
        dirnumber[0] += 1
        return open_fs(str(path), create=True)
    monkeypatch.setattr(testrunner, '_configure_backing_store', localfs)
    testrunner.backup()

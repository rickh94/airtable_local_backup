import os
from pathlib import Path
import pytest

from airtable_local_backup import runner
from airtable_local_backup.exceptions import ConfigurationError

HERE = os.path.dirname(__file__)
DATA = Path(HERE, 'testdata')


@pytest.fixture
def testconf_yml():
    return os.path.abspath(Path(DATA, 'testconf.yml'))


@pytest.fixture
def badconf_yml():
    return os.path.abspath(Path(DATA, 'bad.yml'))


@pytest.fixture
def testrunner(testconf_yml):
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
    assert testrunner.config['Attachment Store']['Type'] == 'S3-compat'
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

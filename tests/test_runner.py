import os
from pathlib import Path
import pytest

from airtable_local_backup import runner

HERE = os.path.dirname(__file__)
DATA = Path(HERE, 'testdata')


@pytest.fixture
def testconf_yml():
    return os.path.abspath(Path(DATA, 'testconf.yml'))


def test_config(testconf_yml):
    testrunner = runner.Runner(path=testconf_yml)
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

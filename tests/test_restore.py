import os
from pathlib import Path
from unittest import mock
import pytest
from airtable_local_backup import restore


def test_prepare_records(lots_of_fields_correct, filedata, monkeypatch,
                         tmpdir):
    """Tests prepare_records. mock the dependency injection.
    """
    def tempfile(path, mode):
        return open(Path(tmpdir, path), mode)
    fakes3 = mock.MagicMock()
    fakes3.geturl.return_value = 'http://example.com/object'
    fakeopen = mock.MagicMock()
    monkeypatch.setattr(fakes3, 'open', tempfile)
    fakeopen.return_value = mock.MagicMock()
    newrecords = list(restore.prepare_records(lots_of_fields_correct,
                                              s3fs=fakes3,
                                              check_integrity=True))
    expectedcontent = filedata.values()
    testcontent = []
    for item in os.listdir(tmpdir):
        with open(Path(tmpdir, item), 'r') as content:
            testcontent.append(content.read())
    assert set(expectedcontent) == set(testcontent),\
        "content of written files should match content of original files"

    assert fakes3.geturl.call_count == len(expectedcontent),\
        "there should be one geturl call per file"
    # assert len(fakes3.geturl.call_list()) == len(filedata)

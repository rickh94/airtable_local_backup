import json
import pytest


@pytest.fixture
def lots_of_fields_raw():
    with open('lots_of_fields_raw.json', 'r') as jsonfile:
        fake_tabledata = json.load(jsonfile)
    return fake_tabledata


@pytest.fixture
def lots_of_fields_hashes():
    with open('hashes.json', 'r') as jsonfile:
        return json.load(jsonfile)


def test_download_table(lots_of_fields_raw, lots_of_fields_hashes):
    pass


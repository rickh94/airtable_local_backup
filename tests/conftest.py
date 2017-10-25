import pytest
import json
import os
from pathlib import Path

HERE = os.path.dirname(__file__)
DATA = Path(HERE, 'testdata')


@pytest.fixture
def lots_of_fields_raw():
    with open(Path(DATA, 'lots_of_fields_raw.json'), 'r') as jsonfile:
        return json.load(jsonfile)


@pytest.fixture
def lots_of_fields_hashes():
    with open(Path(DATA, 'hashes.json'), 'r') as jsonfile:
        return json.load(jsonfile)


@pytest.fixture
def filedata():
    with open(Path(DATA, 'filedata.json'), 'r') as jsonfile:
        return json.load(jsonfile)


@pytest.fixture
def lots_of_fields_correct():
    with Path(DATA, 'lots_of_fields.json').open(mode='r') as jsonfile:
        return json.load(jsonfile)

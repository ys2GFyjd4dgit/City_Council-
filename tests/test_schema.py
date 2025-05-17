import json
import glob
import os
from . import jsonschema

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schema', 'municipal_councillor_v1.1.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

with open(SCHEMA_PATH, encoding='utf-8') as f:
    SCHEMA = json.load(f)

json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))


def test_files_exist():
    assert json_files, 'No JSON files found in processed data directory'


import pytest
@pytest.mark.parametrize('path', json_files)
def test_validate_file(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)
    for item in data:
        jsonschema.validate(item, SCHEMA)

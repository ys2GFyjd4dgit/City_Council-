import glob
import json
import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT_DIR)
from tests.jsonschema import validate, ValidationError

SCHEMA_PATH = os.path.join(ROOT_DIR, 'schema', 'municipal_councillor_v1.1.json')
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'processed')


def main():
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema = json.load(f)

    json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    if not json_files:
        print('No JSON files found in processed data directory')
        return 1

    for path in json_files:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f'{path}: file does not contain a list of objects')
            return 1
        for item in data:
            try:
                validate(item, schema)
            except ValidationError as e:
                print(f'{path}: {e}')
                return 1
    print('All files valid')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

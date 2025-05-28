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
    # スキーマの選択（v1.2を優先）
    schema_v12 = os.path.join(ROOT_DIR, 'schema', 'municipal_councillor_v1.2.json')
    if os.path.exists(schema_v12):
        schema_path = schema_v12
        print("Using schema v1.2")
    else:
        schema_path = SCHEMA_PATH
        print("Using schema v1.1")
    
    try:
        with open(schema_path, encoding='utf-8') as f:
            schema = json.load(f)
    except Exception as e:
        print(f'Error loading schema: {e}')
        return 1

    # 都道府県別ディレクトリに対応
    json_files = glob.glob(os.path.join(DATA_DIR, '*.json'))
    json_files.extend(glob.glob(os.path.join(DATA_DIR, '*', '*.json')))
    
    if not json_files:
        print('No JSON files found in processed data directory')
        return 1

    errors = []
    warnings = []
    
    for path in json_files:
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f'{path}: Invalid JSON - {e}')
            continue
            
        if not isinstance(data, list):
            errors.append(f'{path}: file does not contain a list of objects')
            continue
            
        if len(data) == 0:
            warnings.append(f'{path}: Empty data (no council members)')
            continue
            
        # v1.2スキーマの場合は配列全体を検証
        if "v1.2" in schema_path:
            try:
                validate(data, schema)
            except ValidationError as e:
                errors.append(f'{path}: {e}')
        else:
            # v1.1スキーマの場合は各要素を検証
            for i, item in enumerate(data):
                try:
                    validate(item, schema)
                except ValidationError as e:
                    errors.append(f'{path}[{i}]: {e}')
    
    # 結果表示
    if errors:
        print(f"\n❌ Found {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
            
    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warnings:")
        for warning in warnings:
            print(f"  - {warning}")
            
    if not errors:
        print(f"\n✅ All {len(json_files)} files are valid!")
        if warnings:
            return 0  # 警告があっても成功
        
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())

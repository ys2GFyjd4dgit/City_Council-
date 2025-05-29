#!/usr/bin/env python3
"""
HTMLビューア用のデータファイル(data.js)と各自治体の詳細データを自動生成するスクリプト
JSONファイルから議員数とX登録数を集計し、JavaScriptファイルを生成する
"""

import json
import os
from pathlib import Path
from datetime import datetime

def load_json_file(file_path):
    """JSONファイルを読み込む"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_municipality_info(json_path):
    """ファイル名から自治体情報を取得"""
    filename = json_path.stem
    parts = filename.split('_')
    
    if len(parts) >= 3:
        code = parts[1]
        municipality_name = parts[2]
        return code, municipality_name
    
    return None, None

def count_x_accounts(members):
    """X登録数をカウント"""
    return sum(1 for member in members if member.get('X（旧Twitter）') and member['X（旧Twitter）'] != 'null')

def escape_js_string(s):
    """JavaScript文字列用にエスケープ"""
    if s is None:
        return 'null'
    return json.dumps(s, ensure_ascii=False)

def generate_municipality_js(output_path, code, members):
    """各自治体の詳細データJSファイルを生成"""
    
    js_content = f"""// 議員データ - {code} （{datetime.now().strftime('%Y年%m月%d日')}更新）
// このファイルは scripts/update_viewer_data.py により自動生成されます

window.municipalityMembers_{code} = [
"""
    
    # 議員データを追加
    member_entries = []
    for member in members:
        x_account = member.get('X（旧Twitter）')
        if x_account and x_account != 'null':
            x_value = escape_js_string(x_account)
        else:
            x_value = 'null'
            
        entry = f"""    {{
        "氏名": {escape_js_string(member.get('氏名', ''))},
        "よみ": {escape_js_string(member.get('よみ', ''))},
        "所属": {escape_js_string(member.get('所属', '無所属'))},
        "X（旧Twitter）": {x_value}
    }}"""
        member_entries.append(entry)
    
    js_content += ",\n".join(member_entries)
    js_content += "\n];\n"
    
    # ディレクトリを作成
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ファイルに書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

def generate_data_js(output_path, municipality_data):
    """data.jsファイルを生成"""
    
    # JavaScriptコードを生成
    js_content = f"""// 議員データ（{datetime.now().strftime('%Y年%m月%d日')}更新）
// このファイルは scripts/update_viewer_data.py により自動生成されます
// 手動で編集しないでください

const municipalityData = {{
"""
    
    # 自治体データを追加
    entries = []
    for code, data in sorted(municipality_data.items()):
        entry = f"    '{code}': {{ name: '{data['name']}', prefecture: '{data['prefecture']}', count: {data['count']}, xCount: {data['xCount']} }}"
        entries.append(entry)
    
    js_content += ",\n".join(entries)
    js_content += "\n};\n"
    
    # ファイルに書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Generated: {output_path}")

def main():
    # プロジェクトのルートディレクトリを取得
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data" / "processed"
    viewer_dir = project_root / "viewer"
    output_path = viewer_dir / "js" / "data.js"
    municipalities_dir = viewer_dir / "js" / "municipalities"
    
    # 都道府県マップ
    prefecture_map = {
        "11": "11_埼玉県",
        "13": "13_東京都"
    }
    
    municipality_data = {}
    total_municipalities = 0
    total_members = 0
    total_x_accounts = 0
    
    # すべての都道府県ディレクトリを処理
    for pref_dir in data_dir.iterdir():
        if not pref_dir.is_dir():
            continue
            
        # JSONファイルを処理
        for json_path in pref_dir.glob("議員リスト_*.json"):
            # CSVファイルをスキップ
            if json_path.suffix != '.json':
                continue
                
            try:
                # 自治体情報を取得
                code, municipality_name = get_municipality_info(json_path)
                if not code:
                    continue
                
                # JSONデータを読み込み
                members = load_json_file(json_path)
                
                # 統計情報を計算
                member_count = len(members)
                x_account_count = count_x_accounts(members)
                
                # 都道府県を判定
                prefecture_code = code[:2]
                prefecture = prefecture_map.get(prefecture_code, f"{prefecture_code}_不明")
                
                # データを保存
                municipality_data[code] = {
                    'name': municipality_name,
                    'prefecture': prefecture,
                    'count': member_count,
                    'xCount': x_account_count
                }
                
                # 各自治体の詳細データファイルを生成
                municipality_js_path = municipalities_dir / f"{code}.js"
                generate_municipality_js(municipality_js_path, code, members)
                
                # 統計を更新
                total_municipalities += 1
                total_members += member_count
                total_x_accounts += x_account_count
                
                print(f"処理完了: {municipality_name} - 議員数: {member_count}, X登録: {x_account_count}")
                
            except Exception as e:
                print(f"エラー: {json_path} - {e}")
    
    # data.jsを生成
    generate_data_js(output_path, municipality_data)
    
    # 統計情報を表示
    print("\n" + "="*50)
    print(f"総自治体数: {total_municipalities}")
    print(f"総議員数: {total_members}")
    print(f"X登録数: {total_x_accounts} ({total_x_accounts/total_members*100:.1f}%)")
    print("="*50)

if __name__ == "__main__":
    main()

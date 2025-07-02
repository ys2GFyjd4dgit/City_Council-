#!/usr/bin/env python3
"""
議員データJSONファイルを読み込んで、ビューア用のdata.jsファイルを生成するスクリプト
"""

import json
import glob
import os
from datetime import datetime
import sys

def extract_prefecture_info(filepath):
    """ファイルパスから都道府県情報を抽出"""
    parts = filepath.split(os.sep)
    
    # data/processed/11_埼玉県/議員リスト_112089_所沢市.json のような形式
    if len(parts) > 3 and "_" in parts[-2]:
        prefecture = parts[-2]
        return prefecture
    
    # data/processed/議員リスト_132012_八王子市.json のような形式（東京都の場合）
    filename = parts[-1]
    if filename.startswith("議員リスト_13"):
        return "13_東京都"
    
    return None

def generate_viewer_data():
    """viewer/js/data.js ファイルを生成"""
    
    # 都道府県ごとのデータを格納
    prefecture_data = {}
    
    # 議員データのJSONファイルを検索（一度の操作で両パターンを取得）
    json_files = glob.glob("data/processed/*.json") + glob.glob("data/processed/*/*.json")
    
    # CSVファイルなどは除外
    json_files = [f for f in json_files if f.endswith(".json") and "議員リスト_" in f]
    
    print(f"Found {len(json_files)} JSON files")
    
    for filepath in sorted(json_files):
        try:
            # ファイル名から情報を抽出
            filename = os.path.basename(filepath)
            parts = filename.replace("議員リスト_", "").replace(".json", "").split("_")
            
            if len(parts) < 2:
                print(f"Skipping invalid filename: {filename}")
                continue
                
            code = parts[0]
            municipality = parts[1]
            
            # 都道府県情報を取得
            prefecture = extract_prefecture_info(filepath)
            if not prefecture:
                print(f"Could not extract prefecture from: {filepath}")
                continue
            
            # JSONファイルを読み込み
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 議員数とX登録数をカウント
            total_count = len(data)
            x_count = sum(1 for member in data if member.get("X（旧Twitter）"))
            
            # データを格納
            if prefecture not in prefecture_data:
                prefecture_data[prefecture] = {}
            
            prefecture_data[prefecture][code] = {
                "name": municipality,
                "prefecture": prefecture,
                "count": total_count,
                "xCount": x_count
            }
            
            print(f"Processed: {municipality} ({prefecture}) - {total_count} members, {x_count} with X")
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue
    
    # data.js ファイルを生成
    output_lines = []
    output_lines.append(f"// 議員データ（{datetime.now().strftime('%Y年%m月%d日')}現在）")
    output_lines.append("const municipalityData = {")
    
    # 都道府県順にソート
    for prefecture in sorted(prefecture_data.keys()):
        # 都道府県名をコメントとして追加
        pref_name = prefecture.split("_")[1] if "_" in prefecture else prefecture
        output_lines.append(f"    // {pref_name}")
        
        # 自治体コード順にソート
        for code in sorted(prefecture_data[prefecture].keys()):
            data = prefecture_data[prefecture][code]
            line = f"    '{code}': {{ name: '{data['name']}', prefecture: '{data['prefecture']}', count: {data['count']}, xCount: {data['xCount']} }},"
            output_lines.append(line)
        
        output_lines.append("")  # 空行を追加
    
    # 最後のカンマを削除
    if output_lines[-2].endswith(","):
        output_lines[-2] = output_lines[-2][:-1]
    
    output_lines.append("};")
    output_lines.append("")
    output_lines.append(f"// Last updated: {datetime.now().isoformat()}")
    
    # ファイルに書き込み
    output_path = "viewer/js/data.js"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    print(f"\nGenerated {output_path}")
    print(f"Total prefectures: {len(prefecture_data)}")
    print(f"Total municipalities: {sum(len(p) for p in prefecture_data.values())}")

if __name__ == "__main__":
    # スクリプトのディレクトリから実行する場合とプロジェクトルートから実行する場合の両方に対応
    if os.path.exists("data/processed"):
        generate_viewer_data()
    elif os.path.exists("../data/processed"):
        os.chdir("..")
        generate_viewer_data()
    else:
        print("Error: Could not find data/processed directory")
        print("Please run this script from the project root or scripts directory")
        sys.exit(1)

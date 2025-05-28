#!/usr/bin/env python3
"""
既存のファイルを都道府県別ディレクトリ構造に移行するスクリプト

実行前に必ずバックアップを取ってください。
"""

import os
import shutil
import json
from pathlib import Path

# 都道府県コードと名前のマッピング
PREFECTURE_MAP = {
    "13": "13_東京都",
    "11": "11_埼玉県",
}

def get_prefecture_code(municipality_code):
    """自治体コードから都道府県コードを取得"""
    return municipality_code[:2]

def migrate_processed_files():
    """processedディレクトリのファイルを移行"""
    processed_dir = Path("data/processed")
    
    # 既存のJSONファイルを収集
    json_files = list(processed_dir.glob("議員リスト_*.json"))
    
    if not json_files:
        print("移行するファイルがありません。")
        return
    
    print(f"{len(json_files)}個のファイルを移行します。")
    
    for json_file in json_files:
        # ファイル名から自治体コードを抽出
        filename = json_file.name
        parts = filename.split("_")
        if len(parts) >= 2:
            municipality_code = parts[1]
            prefecture_code = get_prefecture_code(municipality_code)
            
            if prefecture_code in PREFECTURE_MAP:
                # 新しいディレクトリを作成
                new_dir = processed_dir / PREFECTURE_MAP[prefecture_code]
                new_dir.mkdir(parents=True, exist_ok=True)
                
                # ファイルを移動
                new_path = new_dir / filename
                print(f"移動: {json_file} -> {new_path}")
                shutil.move(str(json_file), str(new_path))
            else:
                print(f"警告: 未知の都道府県コード {prefecture_code} ({filename})")

def migrate_raw_files():
    """rawディレクトリのファイルを移行"""
    raw_dir = Path("data/raw")
    
    # 東京都の市町村リスト（現在のデータから）
    tokyo_municipalities = {
        "八王子市", "立川市", "武蔵野市", "三鷹市", "青梅市", "府中市", 
        "昭島市", "調布市", "町田市", "小金井市", "小平市", "日野市",
        "東村山市", "国分寺市", "国立市", "福生市", "狛江市", "東大和市",
        "清瀬市", "東久留米市", "武蔵村山市", "多摩市", "稲城市", "羽村市",
        "あきる野市", "西東京市", "瑞穂町", "日の出町", "檜原村", "奥多摩町",
        "大島町", "利島村", "新島村", "神津島村", "三宅村", "御蔵島村",
        "八丈町", "青ヶ島村", "小笠原村"
    }
    
    for municipality_dir in raw_dir.iterdir():
        if municipality_dir.is_dir() and municipality_dir.name in tokyo_municipalities:
            # 東京都のディレクトリを作成
            tokyo_dir = raw_dir / "13_東京都"
            tokyo_dir.mkdir(parents=True, exist_ok=True)
            
            # ディレクトリを移動
            new_path = tokyo_dir / municipality_dir.name
            print(f"移動: {municipality_dir} -> {new_path}")
            shutil.move(str(municipality_dir), str(new_path))

def update_readme_links():
    """README.mdのリンクを更新する処理のプレースホルダー"""
    print("\n注意: README.mdのリンクは手動で更新してください。")
    print("例: data/processed/議員リスト_xxx.json")
    print(" -> data/processed/13_東京都/議員リスト_xxx.json")

def main():
    """メイン処理"""
    print("都道府県別ディレクトリ構造への移行を開始します。")
    
    response = input("\n実行しますか？ (y/n): ")
    if response.lower() != 'y':
        print("キャンセルしました。")
        return
    
    # ファイル移行を実行
    migrate_processed_files()
    migrate_raw_files()
    update_readme_links()
    
    print("\n移行が完了しました。")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
データ品質をチェックし、改善点を報告するスクリプト
"""

import json
import os
import glob
from collections import defaultdict
from datetime import datetime

def check_x_accounts():
    """Xアカウントの登録状況を分析"""
    stats = defaultdict(lambda: {"total": 0, "with_x": 0})
    
    # 都道府県別ディレクトリに対応
    json_files = glob.glob("data/processed/*.json")
    json_files.extend(glob.glob("data/processed/*/*.json"))
    for filepath in json_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        filename = os.path.basename(filepath)
        municipality = filename.split("_")[2].replace(".json", "")
        
        for member in data:
            stats[municipality]["total"] += 1
            if member.get("X（旧Twitter）"):
                stats[municipality]["with_x"] += 1
    
    return stats

def check_missing_data():
    """欠損データをチェック"""
    issues = []
    
    # 空のJSONファイルをチェック
    json_files = glob.glob("data/processed/*.json")
    json_files.extend(glob.glob("data/processed/*/*.json"))
    for filepath in json_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            issues.append(f"空のデータ: {os.path.basename(filepath)}")
    
    # rawディレクトリで対応するprocessedがないものをチェック
    # 都道府県別ディレクトリに対応
    raw_dirs = []
    for item in os.listdir("data/raw"):
        item_path = os.path.join("data/raw", item)
        if os.path.isdir(item_path):
            if item.startswith(("11_", "13_")):  # 都道府県ディレクトリ
                for subitem in os.listdir(item_path):
                    if os.path.isdir(os.path.join(item_path, subitem)):
                        raw_dirs.append(subitem)
            else:
                raw_dirs.append(item)
    
    processed_files = []
    for f in glob.glob("data/processed/*.json"):
        processed_files.append(os.path.basename(f).split("_")[2].replace(".json", ""))
    for f in glob.glob("data/processed/*/*.json"):
        processed_files.append(os.path.basename(f).split("_")[2].replace(".json", ""))
    
    for raw_dir in raw_dirs:
        if raw_dir not in processed_files:
            issues.append(f"処理済みデータなし: {raw_dir}")
    
    return issues

def check_data_freshness():
    """データの鮮度をチェック"""
    freshness = {}
    
    # README.mdから最終更新日を抽出（簡易版）
    # 実際にはREADMEをパースして日付を取得
    
    return freshness

def generate_report():
    """品質レポートを生成"""
    print("=== データ品質レポート ===")
    print(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Xアカウント統計
    print("## Xアカウント登録状況")
    x_stats = check_x_accounts()
    total_members = sum(s["total"] for s in x_stats.values())
    total_with_x = sum(s["with_x"] for s in x_stats.values())
    
    print(f"総議員数: {total_members}")
    print(f"X登録数: {total_with_x} ({total_with_x/total_members*100:.1f}%)\n")
    
    # 登録率の低い自治体TOP5
    print("### X登録率の低い自治体（改善候補）")
    low_x_municipalities = sorted(
        [(m, s["with_x"]/s["total"]*100) for m, s in x_stats.items() if s["total"] > 0],
        key=lambda x: x[1]
    )[:5]
    
    for municipality, rate in low_x_municipalities:
        members = x_stats[municipality]
        print(f"- {municipality}: {members['with_x']}/{members['total']} ({rate:.1f}%)")
    
    print("\n## データの問題点")
    issues = check_missing_data()
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("- 問題なし")
    
    print("\n## 推奨アクション")
    print("1. 青ヶ島村の議員データを収集")
    print("2. X登録率0%の自治体のアカウントを再調査")
    print("3. 八王子市、武蔵村山市のrawデータを追加")
    print("4. 古いデータ（30日以上）の更新を検討")

if __name__ == "__main__":
    generate_report()
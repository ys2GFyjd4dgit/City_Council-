#!/usr/bin/env python3
"""
Xアカウント検索支援ツール
市議会議員のXアカウントを効率的に検索するためのヘルパースクリプト
"""

import json
import sys
from pathlib import Path

def load_council_data(json_path):
    """議員リストJSONを読み込む"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_search_queries(member):
    """議員情報から検索クエリを生成"""
    name = member['氏名'].replace('　', '')
    reading = member['よみ'].replace(' ', '')
    party = member.get('所属', '')
    
    queries = [
        f'"{name}" 市議 site:x.com',
        f'"{name}" 市議会',
        f'{name} {party} 議員',
        f'@{reading[:4]}',  # 読みの最初の4文字でユーザー名検索
        f'@{name[:2]}',     # 名前の最初の2文字でユーザー名検索
    ]
    
    return queries

def check_existing_accounts(data):
    """既存のXアカウント情報を確認"""
    with_account = []
    without_account = []
    
    for member in data:
        if member.get('X（旧Twitter）'):
            with_account.append(member)
        else:
            without_account.append(member)
    
    return with_account, without_account

def print_search_suggestions(json_path):
    """検索候補を表示"""
    data = load_council_data(json_path)
    with_account, without_account = check_existing_accounts(data)
    
    print(f"総議員数: {len(data)}")
    print(f"Xアカウント登録済み: {len(with_account)}")
    print(f"未登録: {len(without_account)}")
    print("\n" + "="*50 + "\n")
    
    # 既存アカウントのある議員を表示（フォロー関係確認用）
    if with_account:
        print("【Xアカウント登録済み議員】")
        print("これらの議員のフォロー/フォロワーを確認してください：")
        for member in with_account:
            print(f"- {member['氏名']} ({member['所属']}): {member['X（旧Twitter）']}")
        print("\n" + "="*50 + "\n")
    
    # 未登録議員の検索クエリを生成
    print("【Xアカウント未登録議員の検索候補】")
    for member in without_account:
        print(f"\n◆ {member['氏名']} ({member['よみ']}) - {member['所属']}")
        queries = generate_search_queries(member)
        print("検索クエリ:")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")

def main():
    if len(sys.argv) < 2:
        print("使用方法: python search_x_accounts.py <議員リストJSONファイル>")
        print("例: python search_x_accounts.py data/processed/議員リスト_132233_武蔵村山市.json")
        sys.exit(1)
    
    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"エラー: ファイルが見つかりません - {json_path}")
        sys.exit(1)
    
    print_search_suggestions(json_path)

if __name__ == "__main__":
    main()
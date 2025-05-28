#!/usr/bin/env python3
"""
README.mdのリンクを都道府県別ディレクトリ構造に更新するスクリプト
"""

import re

def update_readme():
    """README.mdのリンクを更新"""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 東京都のリンクを更新
    # data/processed/議員リスト_13xxxx_*.json -> data/processed/13_東京都/議員リスト_13xxxx_*.json
    pattern = r'data/processed/(議員リスト_13\d{4}_[^.]+\.json)'
    replacement = r'data/processed/13_東京都/\1'
    
    updated_content = re.sub(pattern, replacement, content)
    
    # 変更があった場合のみ書き込み
    if content != updated_content:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("README.mdのリンクを更新しました。")
        
        # 変更箇所を表示
        changes = len(re.findall(pattern, content))
        print(f"{changes}箇所のリンクを更新しました。")
    else:
        print("更新するリンクはありませんでした。")

if __name__ == "__main__":
    update_readme()
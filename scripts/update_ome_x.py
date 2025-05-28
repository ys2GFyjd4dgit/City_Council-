#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "片谷　洋夫": "https://x.com/hirookataya"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132055_青梅市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132055_青梅市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"青梅市: {len(x_accounts)}名のXアカウントを更新しました")
#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "馬場　貴大": "https://x.com/babatakahiro802",
    "田原　秀夫": "https://x.com/hideo0814",
    "柴田　雄大": "https://x.com/sca1997728"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132012_八王子市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132012_八王子市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"八王子市: {len(x_accounts)}名のXアカウントを更新しました")
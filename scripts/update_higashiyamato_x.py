#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "大后　治雄": "https://x.com/daigoharuo",
    "上林　真佐恵": "https://x.com/masaekami",
    "大川　元": "https://x.com/hajime1826",
    "中間　建二": "https://x.com/minnanonakama"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132209_東大和市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132209_東大和市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"東大和市: {len(x_accounts)}名のXアカウントを更新しました")
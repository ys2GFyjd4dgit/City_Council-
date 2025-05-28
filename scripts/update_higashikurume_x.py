#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "阿部　利恵子": "https://x.com/abe_rieko",
    "梶井　琢太": "https://twitter.com/kajiitakuta",
    "岩崎　さやこ": "https://x.com/iwasakiiwamo",
    "かやま　玲子": "https://twitter.com/kayamareiwa",
    "高橋　和義": "https://x.com/Kazu44Tak",
    "島崎　孝": "https://x.com/simazakitakasi"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132225_東久留米市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132225_東久留米市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"東久留米市: {len(x_accounts)}名のXアカウントを更新しました")
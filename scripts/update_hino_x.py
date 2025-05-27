#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "岡田　じゅん子": "https://x.com/jokada_hino",
    "新井　ともはる": "https://x.com/tomoharu_arai",
    "伊東　秀章": "https://x.com/hideakiito_hino",
    "伊藤　あゆみ": "https://x.com/AyumiIto55",
    "森沢　美和子": "https://x.com/morisawa_miwako",
    "池田　としえ": "https://x.com/m8BIOzfZ6VaZRDA",
    "峯岸　弘行": "https://x.com/kyokucho313",
    "窪田　知子": "https://x.com/kubotahino"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132128_日野市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132128_日野市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"日野市: {len(x_accounts)}名のXアカウントを更新しました")
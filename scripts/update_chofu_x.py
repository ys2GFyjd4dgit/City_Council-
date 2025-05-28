#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "田村　ゆう子": "https://x.com/t_yuko0v0",
    "鮎川　有祐": "https://x.com/ayukawa0121",
    "大野　祐司": "https://x.com/yujiohno421",
    "榊原　登志子": "https://x.com/toshikobus44",
    "澤井　慧": "https://x.com/KaySawai"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132080_調布市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132080_調布市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"調布市: {len(x_accounts)}名のXアカウントを更新しました")
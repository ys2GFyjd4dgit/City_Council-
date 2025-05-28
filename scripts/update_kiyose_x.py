#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "星野　玲子": "https://x.com/05kiyose",
    "穴見　れいな": "https://x.com/reinakiyosejcp",
    "城野　けんいち": "https://x.com/kenichi_jyono",
    "小西　みか": "https://x.com/mika18_konitan",
    "佐々木　あつ子": "https://x.com/atuko_sasaki"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132217_清瀬市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132217_清瀬市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"清瀬市: {len(x_accounts)}名のXアカウントを更新しました")
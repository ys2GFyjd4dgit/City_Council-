#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "美座　たかあき": "https://twitter.com/mizatakaaki",
    "内山　真吾": "https://twitter.com/boxer_shingo",
    "渡辺　純也": "https://x.com/junya_w",
    "大島　ひろし": "https://x.com/oshimaaki4",
    "大野　ふびと": "https://x.com/Histrian_LF",
    "ひえの　たかゆき": "https://x.com/hieno_result",
    "八田　一彦": "https://x.com/hattakazuhiko",
    "永井　みつる": "https://x.com/mitsuru_nagai33",
    "なかお　フミヒト": "https://x.com/reiwaOJIchannel"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132071_昭島市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132071_昭島市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"昭島市: {len(x_accounts)}名のXアカウントを更新しました")
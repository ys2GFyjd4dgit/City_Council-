#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "天野　かな": "https://x.com/amanokana_",
    "清水　学": "https://x.com/gaku_koganei",
    "坂井　悦子": "https://twitter.com/sakaietsuko",
    "水上　浩": "https://x.com/mizuhiro8",
    "斉藤　康夫": "https://x.com/saitouyasuo2011",
    "渡辺　大三": "https://x.com/watanabedaizou",
    "片山　薫": "https://x.com/katayamakaoru",
    "森戸　洋子": "https://x.com/jcpyoko"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132101_小金井市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132101_小金井市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"小金井市: {len(x_accounts)}名のXアカウントを更新しました")
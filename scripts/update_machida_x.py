#!/usr/bin/env python3
import json

# 見つかったXアカウント
x_accounts = {
    "秋田　しづか": "https://x.com/machidalabo_sa",
    "小野　りゅうじ": "https://x.com/ono_ryuuji", 
    "小野寺　まなぶ": "https://twitter.com/manabu_onodera",
    "木目田　英男": "https://x.com/kimedahideo1",
    "中川　幸太郎": "https://x.com/quarter_law",
    "矢口　まゆ": "https://twitter.com/machida_mayuyu",
    "森本　せいや": "https://x.com/seiya_morimoto",
    "白川　哲也": "https://x.com/shirakawa_",
    "田中　美穂": "https://x.com/mihot_n_k_",
    "佐々木　智子": "https://x.com/sasakitomoko_",
    "三遊亭　らん丈": "https://x.com/s_ranjo",
    "今村　るか": "https://x.com/rukarukainfo",
    "新井　よしなお": "https://x.com/Y_Arai_Machida",
    "吉田　つとむ": "https://x.com/yoshidaben",
    "山下　てつや": "https://x.com/Tetsuyadeganba",
    "藤田　学": "https://x.com/gaku24h"
}

# JSONファイルを読み込み
with open('data/processed/議員リスト_132098_町田市.json', 'r', encoding='utf-8') as f:
    members = json.load(f)

# Xアカウント情報を更新
for member in members:
    if member['氏名'] in x_accounts:
        member['X（旧Twitter）'] = x_accounts[member['氏名']]

# 更新したJSONを保存
with open('data/processed/議員リスト_132098_町田市.json', 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False, indent=2)

print(f"町田市: {len(x_accounts)}名のXアカウントを更新しました")
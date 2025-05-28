# 作業フロー

## 新しい自治体を追加する完全な手順

### 1. 事前準備

```bash
# メインブランチを最新に
git checkout main
git pull

# 作業ブランチを作成
git checkout -b add-{都道府県名}-{市名}
# 例: git checkout -b add-saitama-tokorozawa
```

### 2. 公式サイトの調査

1. 自治体の公式ウェブサイトを確認
2. 議会または議員紹介のページを探す
3. 議員名簿のURLを特定

### 3. データ収集

```bash
# ディレクトリ作成
mkdir -p data/raw/{市町村名}/$(date +%Y%m%d)

# HTMLをダウンロード
curl -s "{議員名簿URL}" -o data/raw/{市町村名}/$(date +%Y%m%d)/source.html

# 内容確認
less data/raw/{市町村名}/$(date +%Y%m%d)/source.html
```

### 4. JSONファイル作成

1. HTMLから議員情報を抽出
2. 以下の形式でJSONを作成

```json
[
  {
    "氏名": "姓　名",
    "登録名": "姓　名",
    "よみ": "せい　めい",
    "X（旧Twitter）": null,
    "所属": "会派名"
  }
]
```

3. ファイルを保存
```bash
# ファイル名: 議員リスト_{自治体コード}_{自治体名}.json
# 保存先: data/processed/
```

### 5. Xアカウント調査

各議員について:
1. `{議員名} {自治体名} 議員` で検索
2. プロフィールを確認
3. 議会活動の投稿があるか確認
4. 見つかったらJSONを更新

### 6. データ検証

```bash
python scripts/validate_data.py
```

### 7. README.md更新

1. 該当する表に行を追加
2. 統計情報を再計算
3. 更新日を記載

### 8. コミット

```bash
git add -A
git commit -m "$(cat <<'EOF'
{市町村名}の議員リストを追加

- 議員数: XX名
- Xアカウント: XX名

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 9. プルリクエスト

```bash
git push -u origin {ブランチ名}
gh pr create --title "{市町村名}の議員リストを追加" --body "$(cat <<'EOF'
## 概要
{都道府県名}{市町村名}の議員リストを追加しました。

## 追加内容
- 議員数: XX名
- Xアカウント: XX名

## 確認事項
- [ ] JSONフォーマットの検証済み
- [ ] README.mdの更新済み
- [ ] 統計情報の再計算済み

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

## トラブルシューティング

### PDFしかない場合
1. PDFファイルをダウンロード
2. 手動でデータを抽出
3. または、ユーザーに相談

### 議員情報が見つからない場合
1. サイトマップを確認
2. 「議会」「議員」などのキーワードで検索
3. それでも見つからない場合はユーザーに報告

### 文字化けする場合
1. 文字コードを確認
2. 必要に応じて変換
```bash
iconv -f SHIFT-JIS -t UTF-8 source.html > source_utf8.html
```

## チェックリスト

- [ ] 公式サイトからデータ取得
- [ ] JSONファイル作成
- [ ] Xアカウント調査
- [ ] データ検証実行
- [ ] README.md更新
- [ ] コミット作成
- [ ] プルリクエスト作成
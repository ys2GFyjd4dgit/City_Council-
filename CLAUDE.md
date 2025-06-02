# Claude Code 用指示書

このファイルはClaude Codeがこのリポジトリを編集する際の指示書です。

## 重要：作業開始前の確認事項

**日付が重要な作業（コミット、統計更新など）を行う前に、必ず`date`コマンドで現在時刻を確認すること。**

## プロジェクト概要

市町村議会の議員情報を収集・管理するプロジェクトです。

## 基本的な作業フロー

### 1. 新しい自治体の追加

```bash
# 1. ブランチ作成
git checkout -b add-{都道府県名}-{市町村名}

# 2. ディレクトリ作成
mkdir -p data/raw/{市町村名}/$(date +%Y%m%d)

# 3. データ取得
curl -s "{公式サイトURL}" -o data/raw/{市町村名}/$(date +%Y%m%d)/source.html

# 4. JSONファイル作成
# data/processed/議員リスト_{自治体コード}_{自治体名}.json

# 5. README.md更新

# 6. コミット＆プルリクエスト
git add -A
git commit -m "{市町村名}の議員リストを追加"
git push -u origin {ブランチ名}
gh pr create
```

### 2. Xアカウント情報の更新

```bash
# 1. Web検索でXアカウントを調査
# 2. JSONファイルを更新
# 3. README.mdの統計を更新
```

## 重要な規則

### ファイル名
- JSON: `議員リスト_{自治体コード}_{自治体名}.json`
- HTML: `data/raw/{市町村名}/YYYYMMDD/source.html`

### JSONフォーマット
```json
[
  {
    "氏名": "姓　名",
    "登録名": "姓　名",
    "よみ": "せい　めい",
    "X（旧Twitter）": "https://x.com/account または null",
    "所属": "会派名 または 無所属"
  }
]
```

### 文字の扱い
- 姓名の間: 全角スペース
- 文字コード: UTF-8
- 改行コード: LF

## チェックリスト

新しい自治体を追加する際:
- [ ] rawディレクトリにHTMLを保存
- [ ] processedディレクトリにJSONを作成
- [ ] JSONのバリデーション実行
- [ ] README.mdの表を更新
- [ ] 統計情報を再計算
- [ ] プルリクエストを作成

## よく使うコマンド

```bash
# データ検証
python scripts/validate_data.py

# 統計情報の確認
ls data/processed/*.json | wc -l  # 自治体数
cat data/processed/*.json | jq '.[] | select(."X（旧Twitter）" != null)' | wc -l  # X登録数

# Git操作
git checkout -b {ブランチ名}
git add -A
git commit -m "{コミットメッセージ}"
git push -u origin {ブランチ名}
gh pr create --title "{タイトル}" --body "{説明}"
```

## 参考ドキュメント

- `docs/AI_GUIDE.md`: AI向け編集ガイド
- `docs/DATA_FORMAT.md`: データフォーマット仕様
- `docs/MUNICIPALITY_CODES.md`: 自治体コード一覧
- `scripts/x_account_verification.md`: Xアカウント確認ガイドライン
# HTMLビューアの自動更新について

## 概要
議員データ（JSONファイル）が更新されると、HTMLビューアも自動的に更新される仕組みを実装しています。

## 自動更新の仕組み

### 1. 更新スクリプト
`scripts/update_viewer_data.py` が以下の処理を行います：
- すべてのJSONファイルを読み込み
- 議員数とX登録数を集計
- `viewer/js/data.js` を自動生成
- 更新日時を記録

### 2. GitHub Actions
`.github/workflows/update-viewer.yml` により：
- JSONファイルが更新されたときに自動実行
- `data.js` を更新してコミット
- 変更がある場合のみコミット

### 3. 手動更新
必要に応じて手動でも更新可能：

```bash
# ローカルで実行
python3 scripts/update_viewer_data.py

# GitHub Actionsで実行
# GitHubのActionsタブから「Update HTML Viewer Data」を手動実行
```

## データフロー

```
JSONファイル更新
    ↓
GitHub Actions起動
    ↓
update_viewer_data.py実行
    ↓
data.js生成
    ↓
自動コミット
    ↓
GitHub Pages更新
```

## 更新内容
- 議員数の変更
- X登録状況の変更
- 新規自治体の追加
- 更新日時

## トラブルシューティング

### 自動更新されない場合
1. GitHub ActionsがEnabledか確認
2. JSONファイルの形式が正しいか確認
3. Actionsのログを確認

### 手動で更新する場合
```bash
cd City_Council-
python3 scripts/update_viewer_data.py
git add viewer/js/data.js
git commit -m "HTMLビューアのデータを更新"
git push
```
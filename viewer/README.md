# 市議会議員データビューア

このディレクトリには、JSONデータを見やすく表示するためのHTMLビューアが含まれています。

## アクセス方法

### 1. GitHub Pages（推奨）
GitHub Pagesが有効な場合：
```
https://ys2gfyjd4dgit.github.io/City_Council-/viewer/
```

### 2. ローカルで表示
ローカルサーバーを起動して表示する場合：

```bash
# Python 3の場合
python3 -m http.server 8000

# Python 2の場合
python -m SimpleHTTPServer 8000

# Node.jsの場合
npx http-server
```

その後、ブラウザで `http://localhost:8000/viewer/` にアクセス

### 3. ファイルを直接開く
- リポジトリをクローンまたはダウンロード
- `viewer/index.html` をブラウザで開く

## 機能

- **自治体一覧**: すべての自治体を表示
- **議員詳細**: 各自治体の議員情報を表形式で表示
- **検索機能**: 名前や読みで検索
- **ソート機能**: 各列でソート可能
- **フィルター**: 所属政党でフィルタリング
- **レスポンシブデザイン**: スマートフォンにも対応
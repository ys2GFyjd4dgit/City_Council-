# Xアカウント検索ガイド

このガイドでは、市町村議会議員のX（旧Twitter）アカウントを効率的に検索・収集するための方法を説明します。

## 検索ツール一覧

### 1. search_x_accounts.py（基本検索ツール）
シンプルで使いやすい基本的な検索支援ツール。市町村タイプを自動判定します。

```bash
# 使用例
python scripts/search_x_accounts.py data/processed/13_東京都/議員リスト_133078_檜原村.json
```

**特徴:**
- 市議会・町議会・村議会を自動判定
- 基本的な検索クエリを生成
- 既存アカウントのフォロー関係確認を推奨

### 2. search_x_accounts_v2.py（強化版検索ツール）
並列処理と高度な検索戦略を実装した強化版。

```bash
# 単一ファイル処理
python scripts/search_x_accounts_v2.py data/processed/11_埼玉県/議員リスト_112089_所沢市.json

# 都道府県一括処理（並列実行）
python scripts/search_x_accounts_v2.py --prefecture data/processed/13_東京都

# ブラウザで検索タブを開く
python scripts/search_x_accounts_v2.py --browser data/processed/13_東京都/議員リスト_132233_武蔵村山市.json
```

**特徴:**
- 最大4並列で複数自治体を同時処理
- 優先度付き検索戦略（高・中・低）
- バッチ検索URL生成（5名ずつ）
- Markdownレポート自動生成
- ブラウザ自動起動オプション

### 3. automated_x_search.py（自動更新ツール）
見つかったアカウントをJSONファイルに自動更新。

```bash
# 単一ファイル自動処理
python scripts/automated_x_search.py data/processed/13_東京都/議員リスト_132101_小金井市.json

# 全自治体自動処理
python scripts/automated_x_search.py --all

# 特定都道府県のみ
python scripts/automated_x_search.py --prefecture 11  # 埼玉県
```

**特徴:**
- アカウントの妥当性を自動検証
- JSONファイルを自動更新（バックアップ付き）
- 信頼度スコアの算出
- 詳細な処理レポート生成

### 4. comprehensive_x_discovery.py（包括的発見システム）
最も高度な検索戦略を実装。複数の手法を組み合わせて発見率を最大化。

```bash
# 全都道府県の発見計画生成
python scripts/comprehensive_x_discovery.py --all

# 単一自治体の詳細分析
python scripts/comprehensive_x_discovery.py data/processed/13_東京都/議員リスト_132292_西東京市.json
```

**特徴:**
- 5つの検索戦略を統合
  1. 直接検索（名前、読み、所属）
  2. フォロー関係分析
  3. リスト分析
  4. ハッシュタグ分析
  5. メンション分析
- 自治体間の関係グラフ構築
- CSV形式で検索URLを出力
- 優先対象自治体の自動判定

## 検索戦略のベストプラクティス

### 1. 段階的アプローチ

1. **初回スキャン**: `search_x_accounts_v2.py`で都道府県単位の一括処理
2. **詳細検索**: `comprehensive_x_discovery.py`で未発見率の高い自治体を重点調査
3. **自動更新**: `automated_x_search.py`で定期的に新規アカウントをチェック

### 2. 効果的な検索クエリ

#### 基本パターン
- `"議員名" 市議 site:x.com` - 最も基本的で効果的
- `"議員名" 自治体名 議員` - 地域限定検索
- `@読みの最初6文字` - ユーザー名検索

#### 応用パターン
- `所属政党 自治体名 姓` - 政党経由の検索
- `#自治体名選挙 議員名` - 選挙タグ検索
- `議員名 当選` - 選挙結果からの検索

### 3. 検証のポイント

Xアカウントが本人のものか確認する際のチェックポイント：

1. **プロフィール確認**
   - 「○○市議会議員」などの記載
   - 所属政党の記載
   - 自治体名の言及

2. **投稿内容**
   - 議会活動の報告
   - 地域の話題
   - 政策に関する発言

3. **フォロー関係**
   - 同じ自治体の他の議員
   - 自治体公式アカウント
   - 所属政党の関連アカウント

4. **認証・公式性**
   - 議会公式サイトでの掲載
   - 選挙公報での記載
   - 他の議員からのメンション

## 並列処理による高速化

都道府県単位で複数自治体を並列処理する場合：

```bash
# 4並列で東京都の全自治体を処理
python scripts/search_x_accounts_v2.py --prefecture data/processed/13_東京都

# 処理状況の確認
tail -f reports/13_東京都_summary_*.md
```

## トラブルシューティング

### よくある問題と対処法

1. **同姓同名の議員**
   - 自治体名を含めて検索
   - 所属政党で絞り込み
   - 年齢や当選回数を参考に

2. **旧アカウント・非アクティブ**
   - 最終投稿日を確認
   - 新しいアカウントの存在を確認
   - 引退・落選の可能性を考慮

3. **非公開アカウント**
   - フォロワーから推測
   - 他の議員のフォローリストを確認
   - 議会公式リストをチェック

## データ品質の維持

### 定期メンテナンス

```bash
# 月次チェック - 全自治体のX登録率を確認
python scripts/check_data_quality.py --x-coverage

# 四半期チェック - アカウントの有効性確認
python scripts/validate_x_accounts.py --check-active

# 年次チェック - 引退・落選議員の更新
python scripts/update_council_members.py --check-election-results
```

## 今後の改善案

1. **AI/ML統合**
   - プロフィール画像の顔認識
   - 投稿内容の自然言語処理
   - アカウント真正性の自動判定

2. **他SNS対応**
   - Instagram検索機能
   - Facebook検索機能
   - YouTube検索機能

3. **API統合**
   - X API（有料）の活用検討
   - 選挙管理委員会APIとの連携
   - 議会公式サイトのスクレイピング自動化
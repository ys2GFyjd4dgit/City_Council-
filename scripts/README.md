# スクリプト説明

このディレクトリには、プロジェクトで使用する各種スクリプトが含まれています。

## validate_data.py

JSONファイルのバリデーションを行うスクリプトです。

### 使用方法
```bash
python scripts/validate_data.py
```

### チェック内容
- JSONの構文エラー
- 必須フィールドの存在
- データ型の一致
- スキーマとの整合性

## search_x_accounts.py

議員のX（旧Twitter）アカウントを検索・更新するスクリプトです。

### 使用方法
```bash
python scripts/search_x_accounts.py
```

## update_*_x.py

各市町村のXアカウント情報を個別に更新するスクリプト群です。

### 命名規則
`update_{市町村名のローマ字}_x.py`

### 例
- update_hachioji_x.py - 八王子市
- update_tachikawa_x.py - 立川市

## x_account_verification.md

Xアカウントの確認・検証に関するガイドラインです。

### 内容
- 検索方法
- 本人確認の基準
- 更新手順

## 新しいスクリプトを追加する場合

1. スクリプト名は機能を表す明確な名前にする
2. ファイル冒頭にdocstringで説明を記載
3. このREADME.mdに説明を追加

### テンプレート
```python
#!/usr/bin/env python3
"""
スクリプトの説明をここに記載
"""

def main():
    # メイン処理
    pass

if __name__ == "__main__":
    main()
```
# プルリクエスト作成手順

## 基本的な流れ

1. **新しいブランチを作成**
   ```bash
   git checkout -b feature/新機能名
   # または
   git checkout -b fix/修正内容
   ```

2. **変更を加える**
   - ファイルを編集
   - 新しいファイルを追加など

3. **変更をステージング**
   ```bash
   git add 変更したファイル
   # または全ての変更を追加
   git add -A
   ```

4. **コミット**
   ```bash
   git commit -m "変更内容の説明"
   ```

5. **ブランチをpush**
   ```bash
   git push -u origin ブランチ名
   ```

6. **プルリクエストを作成**
   ```bash
   gh pr create --title "タイトル" --body "説明"
   ```

## 注意事項

- **mainブランチに直接コミットしない**
- 変更は必ず新しいブランチで行う
- プルリクエストを作成してからマージする

## 例：X未登録議員一覧を更新する場合

```bash
# 1. 新しいブランチを作成
git checkout -b update/unregistered-list

# 2. スクリプトを実行
python3 scripts/generate_unregistered_list.py

# 3. 変更をコミット
git add manual_search/x未登録議員一覧.txt
git commit -m "X未登録議員一覧を更新"

# 4. ブランチをpush
git push -u origin update/unregistered-list

# 5. プルリクエストを作成
gh pr create --title "X未登録議員一覧を更新" --body "最新の登録状況を反映"
```
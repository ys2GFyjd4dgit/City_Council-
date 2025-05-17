# （東京都）市町村議会の情報
- 市町村議会の議事録まとめ
- 市町村議会 所属議員のX（旧Twitter）アカウントまとめ

※data/raw には自治体ごとに日付を付けたサブフォルダを作成し、元ファイルをそのまま保存 例：data/raw/小平市/20250515_source.html
ディレクトリのみを保持するため、空ディレクトリには `.gitkeep` を置く

※data/processed に成果物 JSON を配置
命名規則：議員リスト_{自治体コード6桁}_{自治体名}.json

## Contributing
1. Add a remote repository with `git remote add origin <URL>` if your local clone does not yet have one.
2. Use clear commit messages that briefly summarize the change. For example, `Add official website field to 小平市 council list`.
3. Commit your changes, push them to a branch on the remote, and open a pull request on the hosting platform.

## Tests

If `pytest` is installed, run the test suite from the repository root:

```bash
pytest
```

These tests load files in `data/processed` and validate them against
`schema/municipal_councillor_v1.1.json`.

For environments without `pytest`, the same validation can be performed using:

```bash
python scripts/validate_data.py
```

# City Council Repository Makefile

.PHONY: help validate stats quality add-city test clean viewer-data update-all

help:
	@echo "利用可能なコマンド:"
	@echo "  make validate    - JSONファイルを検証"
	@echo "  make stats      - 統計レポートを生成"
	@echo "  make quality    - データ品質をチェック"
	@echo "  make add-city   - 新しい自治体を追加"
	@echo "  make test       - テストを実行"
	@echo "  make clean      - 一時ファイルを削除"
	@echo "  make viewer-data - ビューア用データを更新"
	@echo "  make update-all  - 全ての更新処理を実行"

validate:
	python scripts/validate_data.py

stats:
	python scripts/generate_statistics.py

quality:
	python scripts/check_data_quality.py

add-city:
	python scripts/add_municipality.py

test:
	python -m pytest tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find data/raw -name "extract_*.py" -delete
	find data/raw -name "parse_*.py" -delete

viewer-data:
	python scripts/update_viewer_data.py

update-all: validate viewer-data stats
	@echo "全ての更新処理が完了しました"
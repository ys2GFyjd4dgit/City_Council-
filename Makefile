# City Council Repository Makefile

.PHONY: help validate stats quality add-city test clean

help:
	@echo "利用可能なコマンド:"
	@echo "  make validate    - JSONファイルを検証"
	@echo "  make stats      - 統計レポートを生成"
	@echo "  make quality    - データ品質をチェック"
	@echo "  make add-city   - 新しい自治体を追加"
	@echo "  make test       - テストを実行"
	@echo "  make clean      - 一時ファイルを削除"

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
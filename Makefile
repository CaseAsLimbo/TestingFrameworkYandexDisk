.PHONY: install install-dev test lint format allure clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	pytest

lint:
	ruff check .

format:
	uv run autoflake -r --in-place --remove-all-unused-imports ./api ./config ./schemas ./tests;
	uv run isort ./api ./config ./schemas ./tests;
	uv run black ./api ./config ./schemas ./tests;

allure:
	pytest --alluredir=allure-results
	allure serve allure-results

clean:
	rm -rf allure-results allure-history .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

.PHONY: setup qa test etl export profile map verify report fmt

VENV=.venv
PY=$(VENV)/Scripts/python

setup:
	python -m venv $(VENV)
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e .
	$(PY) -m pip install ruff mypy pytest

qa:
	ruff check etl_scripts
	mypy etl_scripts
	pytest

test:
	pytest

fmt:
	ruff check --select I --fix .
	ruff check --fix .

export:
	$(PY) etl_scripts/export_excel_sheets_to_csv.py

etl:
	$(PY) etl.py transform --src output --out processed_data

profile:
	$(PY) etl.py profile --src output --out analysis/ai_responses

map:
	$(PY) etl.py map --src processed_data --out processed_data

verify:
	$(PY) etl.py verify --src processed_data --out logs

report:
	$(PY) etl.py verify --src processed_data --out logs


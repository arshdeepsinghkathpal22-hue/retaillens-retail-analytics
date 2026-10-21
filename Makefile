PYTHON ?= python

.PHONY: test demo run download

test:
	$(PYTHON) -m pytest

demo:
	$(PYTHON) scripts/run_pipeline.py --demo

run:
	$(PYTHON) scripts/run_pipeline.py --input "data/raw/Online Retail.xlsx"

download:
	$(PYTHON) scripts/download_data.py

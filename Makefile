VENV=.venv
PYTHON=$(VENV)/bin/python3
PIP=$(VENV)/bin/pip

PROJECT_ROOT=$(shell pwd)
MAIN=daemon/main.py
SIMULATOR=daemon/simulator/simulate_event.py
SMOKE_SCRIPT=scripts/smoke_test.sh

.PHONY: help install run simulate smoke clean

help:
	@echo "Available commands:"
	@echo "  make install   - install dependencies"
	@echo "  make run       - start governance agent"
	@echo "  make simulate  - run event simulator"
	@echo "  make smoke     - run full smoke test"
	@echo "  make clean     - remove caches and logs"

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN)

simulate:
	$(PYTHON) $(SIMULATOR)

smoke:
	bash $(SMOKE_SCRIPT)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f smoke_test_server.log

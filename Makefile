.PHONY: all install populate backend gui run

PYTHON_WIN  = .\venv\Scripts\python.exe
PIP_WIN     = .\venv\Scripts\pip.exe
UVICORN_WIN = .\venv\Scripts\uvicorn.exe

PYTHON_UNIX  = ./venv_linux/bin/python
PIP_UNIX     = ./venv_linux/bin/pip
UVICORN_UNIX = ./venv_linux/bin/uvicorn

# ──────────────────────────────────────────────
# Cible principale : installe, peuple et lance tout
# ──────────────────────────────────────────────

run:
	@echo "Detecting OS..."
	@$(MAKE) _run_$(shell uname -s 2>/dev/null || echo Windows)

_run_Windows:
	python -m venv venv
	$(PIP_WIN) install -r requirements.txt
	$(PYTHON_WIN) app/populate_gui_data.py
	Start-Process powershell -ArgumentList "-NoExit","-Command","$(UVICORN_WIN) app.main:app --port 8000"
	timeout /t 3 /nobreak
	$(PYTHON_WIN) gui\src\main.py

_run_Linux _run_Darwin:
	rm -rf venv_linux
	python3 -m venv venv_linux
	$(PIP_UNIX) install -r requirements.txt
	$(PYTHON_UNIX) app/populate_gui_data.py
	$(UVICORN_UNIX) app.main:app --port 8000 &
	sleep 3
	$(PYTHON_UNIX) gui/src/main.py

# ──────────────────────────────────────────────
# Cibles individuelles (Unix)
# ──────────────────────────────────────────────

install:
	python3 -m venv venv
	$(PIP_UNIX) install -r requirements.txt

populate:
	$(PYTHON_UNIX) app/populate_gui_data.py

backend:
	$(UVICORN_UNIX) app.main:app --port 8000 --reload

gui:
	$(PYTHON_UNIX) gui/src/main.py

# ──────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────

test:
	$(PYTHON_UNIX) -m pytest tests/ -v

test-cov:
	$(PYTHON_UNIX) -m pytest --cov=app tests/

# ──────────────────────────────────────────────
# Nettoyage
# ──────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -f platonAAV.db

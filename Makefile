APP_NAME=psc-ui
SPEC=build/psc-ui.spec
DIST=dist/$(APP_NAME)
EXE=$(DIST)/$(APP_NAME)

.PHONY: help install run build clean distclean lint format test

help:
	@echo "Targets:"
	@echo "  install   - install deps (poetry)"
	@echo "  run       - run UI via python (dev)"
	@echo "  build     - build binary via pyinstaller"
	@echo "  clean     - remove pyinstaller workdir"
	@echo "  distclean - remove dist + build"
	@echo "  lint      - ruff + mypy"
	@echo "  format    - ruff format"
	@echo "  test      - pytest"

install:
	poetry install

run:
	poetry run python -m password_strength_checker.ui.app

build:
	rm -rf build/$(APP_NAME) dist/$(APP_NAME)
	poetry run pyinstaller -y $(SPEC)
	@echo "Built: $(EXE)"

clean:
	rm -rf build/$(APP_NAME)

distclean:
	rm -rf build/$(APP_NAME) dist/$(APP_NAME)

lint:
	poetry run ruff check .
	poetry run mypy src

format:
	poetry run ruff format .

test:
	poetry run pytest

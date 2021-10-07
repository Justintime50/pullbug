PYTHON_BINARY := python3 
VIRTUAL_BIN := venv/bin
PROJECT_NAME := pullbug

## help - Display help about make targets for this Makefile
help:
	@cat Makefile | grep '^## ' --color=never | cut -c4- | sed -e "`printf 's/ - /\t- /;'`" | column -s "`printf '\t'`" -t

## build - Builds the project in preparation for release
build:
	$(PYTHON_BINARY) setup.py sdist bdist_wheel

## coverage - Test the project and generate an HTML coverage report
coverage:
	$(VIRTUAL_BIN)/pytest --cov=$(PROJECT_NAME) --cov-branch --cov-report=html --cov-report=term-missing

## clean - Remove the virtual environment and clear out .pyc files
clean:
	rm -rf ~/.venv/$(PROJECT_NAME)/ venv
	find . -name '*.pyc' -delete
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

## format - Runs the Black Python formatter against the project
format:
	$(VIRTUAL_BIN)/black $(PROJECT_NAME) --skip-string-normalization --line-length 120 --experimental-string-processing
	$(VIRTUAL_BIN)/black test --skip-string-normalization --line-length 120 --experimental-string-processing

## install - Install the project locally
install:
	$(PYTHON_BINARY) -m venv ~/.venv/$(PROJECT_NAME)/
	ln -snf ~/.venv/$(PROJECT_NAME)/ venv
	$(VIRTUAL_BIN)/pip install -e ."[dev]"

## lint - Lint the project
lint:
	$(VIRTUAL_BIN)/flake8 $(PROJECT_NAME)/*.py
	$(VIRTUAL_BIN)/flake8 test/unit/*.py

## test - Test the project
test:
	$(VIRTUAL_BIN)/pytest

.PHONY: help build coverage clean format install lint test

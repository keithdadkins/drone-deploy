.DEFAULT_GOAL := install
.PHONY: install build package coverage test freeze lint smoketest clean purge
PROJ_SLUG = drone_deploy
CLI_NAME = drone-deploy
PY_VERSION = 3.7


OSFLAG 				:=
ifeq ($(OS),Windows_NT)
	OSFLAG += WINDOWS
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		OSFLAG += LINUX
	endif
	ifeq ($(UNAME_S),Darwin)
		OSFLAG += OSX
	endif
endif

OSX: pyinstall
	@mv cli/dist/drone-deploy cli/dist/drone-deploy.x86_64-osx
LINUX: pyinstall
	@mv cli/dist/drone-deploy cli/dist/drone-deploy.x86_64-linux
WINDOWS:
	@echo Building x86_64 'drone-deploy' on Windows

release: $(OSFLAG)

install: requirements build

pyinstall:
	cd cli && \
	pyinstaller drone-deploy.spec --hidden-import=configparser

requirements:
	cd cli && \
	. venv/bin/activate && \
	pip install -r requirements.txt	

build:
	cd cli && \
	pip install --editable .

virtualenv:
	@pip install virtualenv

venv:
	cd cli && \
	virtualenv --python python$(PY_VERSION) venv
	@echo
	@echo To activate the environment, use the following command:
	@echo "source cli/venv/bin/activate"
	@echo
	@echo Once activated, run 'make' to install dependencies and build the cli.
	@echo

freeze:
	cd cli && \
	pipdeptree | grep -P '^\w+' > requirements.txt && \
	sed -i '/drone-deploy/d' requirements.txt

lint:
	cd cli && \
	pylint $(PROJ_SLUG)

smoketest:
	pytest --rootdir=cli --cov-config=cli/.coveragerc -k "smoke" -vv cli/tests

test:
	pytest --rootdir=cli cli/tests

coverage:
	pytest --rootdir=cli --cov-config=cli/.coveragerc --cov=cli -vv cli/tests

clean:
	rm -rf cli/dist \
	rm -rf cli/build \
	rm -rf cli/*.egg-info \
	rm -rf cli/.coverage \
	rm -rf cli/drone_deploy/.coverage

purge: clean
	rm drone-deploy \
	rm -rf venv \
	rm -rf .coverage \
	rm -rf .pytest_cache \
	rm -rf cli/.pytest_cache \
	rm -rf cli/drone_deploy.egg-info \
	rm -rf cli/venv \
	rm -rf cli/__pycache__ \
	rm -rf cli/drone_deploy/__pycache__

testdeployment:
	@drone-deploy new testdeployment

help:
	@echo Make options are:
	@echo make venv - Install and setup a python virtual environment for the project.
	@echo make requirements - Install python project requirements.

.DEFAULT_GOAL := install
.PHONY: install build package coverage test freeze lint smoketest clean purge
PROJ_SLUG = drone_deploy
CLI_NAME = drone-deploy
PY_VERSION = 3.7
GREEN = 2
RED = 1

define colorecho
        @tput bold
        @tput setaf $1
        @echo $2
        @tput sgr0
endef

# TODO
# OSFLAG 				:=
# ifeq ($(OS),Windows_NT)
# 	OSFLAG += WINDOWS
# else
# 	UNAME_S := $(shell uname -s)
# 	ifeq ($(UNAME_S),Linux)
# 		OSFLAG += LINUX
# 	endif
# 	ifeq ($(UNAME_S),Darwin)
# 		OSFLAG += OSX
# 	endif
# endif

# OSX:
# 	@echo "Setting up './drone-deploy' for osx."
# 	@ln -sf cli/dist/drone-deploy.osx drone-deploy
# LINUX:
# 	@echo "Setting up './drone-deploy' for linux."
# 	@ln -sf cli/dist/drone-deploy.linux drone-deploy
# WINDOWS:
# 	@echo "TODO"

# setup_cli: $(OSFLAG)
install: requirements build

requirements:
	cd cli && \
	source venv/bin/activate && \
	pip install -r requirements.txt	

build:
	cd cli && \
	pip install --editable .

virtualenv:
	pip install virtualenv

venv:
	cd cli && \
	virtualenv --python python$(PY_VERSION) venv
	@echo
	@echo To activate the environment, use the following command:
	@echo
	$(call colorecho, $(GREEN), "source cli/venv/bin/activate")
	@echo
	@echo Once activated, you can use the 'install' target to install dependencies:
	@echo
	$(call colorecho, $(GREEN), "source cli/venv/bin/activate")

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

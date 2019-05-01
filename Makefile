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

.PHONY: all

all: setup_cli

OSX:
	@echo "Setting up './drone-deploy' for osx."
	@ln -sf cli/dist/drone-deploy.osx drone-deploy
LINUX:
	@echo "Setting up './drone-deploy' for linux."
	@ln -sf cli/dist/drone-deploy.linux drone-deploy
WINDOWS:
	@echo "TODO"

setup_cli: $(OSFLAG)

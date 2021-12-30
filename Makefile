SHELL = bash

.PHONY: all

all:
	black paks/*.py paks/utils/*.py paks/cli/*.py paks/handlers/*.py

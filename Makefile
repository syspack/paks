SHELL = bash

.PHONY: all

all:
	black paks/*.py paks/utils/*.py paks/cli/*.py paks/handlers/*.py
	pyflakes paks/utils/fileio.py 
	pyflakes paks/utils/terminal.py
	pyflakes paks/*.py
	pyflakes paks/handlers/*.py

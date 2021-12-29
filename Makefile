SHELL = bash

.PHONY: all

all:
	black paks --exclude paks/spack

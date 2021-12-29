SHELL = bash

.PHONY: all

all:
	black paks --exclude paks/spack --exclude paks/sbom.py --exclude env

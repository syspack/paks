__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

__version__ = "0.0.0"
AUTHOR = "Vanessa Sochat, Alec Scott"
NAME = "paks"
PACKAGE_URL = "https://github.com/syspack/paks"
KEYWORDS = "software, GitHub packages."
DESCRIPTION = "GitHub packages package manager."
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = ()

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES

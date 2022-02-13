__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

__version__ = "0.1.1"
AUTHOR = "Vanessa Sochat, Alec Scott"
EMAIL = "vsoch@noreply.github.users.com"
NAME = "paks"
PACKAGE_URL = "https://github.com/syspack/paks"
KEYWORDS = "containers, interactive commands."
DESCRIPTION = "Interactive container commands."
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (
    ("pyaml", {"min_version": None}),
    ("jsonschema", {"min_version": None}),
    ("requests", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES

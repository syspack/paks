__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import paks.utils as utils

install_dir = utils.get_installdir()
reps = {"$install_dir": install_dir, "$root_dir": os.path.dirname(install_dir)}

# The default settings file in the install root
default_settings_file = os.path.join(reps["$install_dir"], "settings.yml")

# Paks home stores user specific keys, etc
pakshome = os.path.expanduser("~/.paks")

# Paks environments
paksenvs = os.path.join(pakshome, "envs")

# The user settings file can be created to over-ride default
user_settings_file = os.path.join(pakshome, "settings.yml")

# Default directory for encrypted environments?
envs_dir = os.path.join(pakshome, "envs")

# Fallback content type
content_type = "application/vnd.paks.container"

# Allowed variables for the environment
allowed_envars = ["username"]

# Default registry prefix to install from
# TODO should we have some kind of pakages here meaning sets of commands?
trusted_packages_registry = "ghcr.io/pakages"

# The GitHub repository for paks
github_url = "https://github.com/syspack/paks"

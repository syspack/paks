__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import paks.utils as utils

install_dir = utils.get_installdir()
reps = {"$install_dir": install_dir, "$root_dir": os.path.dirname(install_dir)}

# The default settings file in the install root
default_settings_file = os.path.join(reps["$install_dir"], "settings.yml")

# Paks home stores user specific keys, etc
pakshome = os.path.expanduser("~/.paks")

# The user settings file can be created to over-ride default
user_settings_file = os.path.join(pakshome, "settings.yml")

# Default directory for keys
keys_dir = os.path.join(pakshome, "keys")

# Allowed variables for the environment
allowed_envars = ["username"]

# The GitHub repository
github_url = "https://github.com/syspack/paks"

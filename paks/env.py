__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
from pathlib import Path
import paks.defaults
import paks.utils
import time
import os


class Environment:
    def __init__(self, config_editor="vim"):
        self.config_editor = config_editor
        self.envars = {}

    def load(self, name):
        """
        Load an environtment by name
        """
        envpath = os.path.join(paks.defaults.paksenvs, name)
        self.ensure_exists(envpath)
        with open(envpath, "r") as fd:
            lines = fd.readlines()
        self.envars = {}
        for line in lines:
            key, value = self.parse_envar(line)
            self.envars[key] = value

    def save(self, envname):
        """
        Save environment by name
        """
        envpath = os.path.join(paks.defaults.paksenvs, envname)
        with open(envpath, "w") as fd:
            for key, value in self.envars.items():
                fd.write("%s=%s" % (key, value))

    def ensure_exists(self, envpath):
        """
        Ensure an envpath exists for an edit or load
        """
        if not os.path.exists(paks.defaults.paksenvs):
            paks.utils.mkdir_p(paks.defaults.paksenvs)
        envpath = os.path.join(paks.defaults.paksenvs, envpath)
        if not os.path.exists(envpath):
            logger.info("Creating %s" % envpath)
            time.sleep(0.5)
            Path(envpath).touch()

    def edit(self, envpath):
        """
        edit a named environment, or create if it doesn't exist.
        """
        self.ensure_exists(envpath)
        envpath = os.path.join(paks.defaults.paksenvs, envpath)

        # Make sure editor exists first!
        editor = paks.utils.which(self.config_editor)
        if not os.path.exists(editor):
            logger.exit(
                "Editor '%s' not found! Update with paks config set config_editor:<name>"
                % self.config_editor
            )
        os.system("%s %s" % (editor, envpath))

    def remove(self, envname, varname):
        """
        Remove a variable from a named environment.
        """
        envpath = os.path.join(paks.defaults.paksenvs, envname)
        if not os.path.exists(envpath):
            logger.error("%s does not exist." % envpath)
            return
        self.load(envname)
        if varname in self.envars:
            del self.envars[varname]
        else:
            logger.error("%s is not found in %s" % (varname, envpath))
            return
        self.save(envname)
        logger.info("%s was removed from environment %s" % (varname, envname))

    def parse_envar(self, param):
        """
        Parse a key value pair (ensure no export)
        """
        key, value = param.split("=", 1)

        # Ensure we remove export
        key = key.replace("export ", "", 1)
        return key.strip(), value.strip()

    def add(self, envname, keyval, force=False):
        """
        Add a variable to a named environment
        """
        if "=" not in keyval:
            logger.error("Expected key=value pair for variable")
            return False
        key, value = self.parse_envar(keyval)
        self.ensure_exists(envname)
        self.load(envname)
        if key in self.envars and not force:
            logger.error(
                "%s is already defined in %s, use --force to overwrite."
                % (key, envname)
            )
            return
        self.envars[key] = value
        self.save(envname)
        logger.info("%s was added to environment %s" % (key, envname))

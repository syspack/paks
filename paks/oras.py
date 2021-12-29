__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import spack.bootstrap
import spack.spec
import spack.util.executable
from paks.logger import logger


class Oras:
    def __init__(self):
        self._oras = None

    @property
    def oras(self):
        if not self._oras:
            with spack.bootstrap.ensure_bootstrap_configuration():
                spec = spack.spec.Spec("oras")
                spack.bootstrap.ensure_executables_in_path_or_raise(
                    ["oras"], abstract_spec=spec
                )
                self._oras = spack.util.executable.which("oras")
        return self._oras

    def push(self, url, save_file):
        """
        Push an oras artifact to an OCI registry
        """
        logger.info("Fetching oras {0}".format(url))
        self.oras("pull", url + ":latest", "--output", os.path.dirname(save_file))

    def fetch(self, url, save_file):
        """Fetch an oras artifact from an OCI registry"""
        logger.info("Fetching oras {0}".format(url))
        self.oras("pull", url + ":latest", "--output", os.path.dirname(save_file))
        return save_file

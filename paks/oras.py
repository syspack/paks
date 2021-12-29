__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import spack.bootstrap
import spack.spec
import paks.utils as utils
import paks.defaults
import spack.util.executable

from paks.logger import logger

import os


class Oras:
    def __init__(self):
        self._oras = None

    @property
    def oras(self):
        """
        Get the oras executable (easier to install on your computer over bootstrap)
        """
        if not self._oras:
            with spack.bootstrap.ensure_bootstrap_configuration():
                spec = spack.spec.Spec("oras")
                spack.bootstrap.ensure_executables_in_path_or_raise(
                    ["oras"], abstract_spec=spec
                )
                self._oras = spack.util.executable.which("oras")
        return self._oras

    def push(self, uri, push_file, content_type=None):
        """
        Push an oras artifact to an OCI registry
        """
        content_type = content_type or paks.defaults.content_type
        logger.info("Pushing oras {0}".format(uri))
        with utils.workdir(os.path.dirname(push_file)):
            self.oras(
                "push",
                uri,
                "--manifest-config",
                "/dev/null:%s" % content_type,
                os.path.basename(push_file),
            )

    def fetch(self, url, save_file):
        """
        Fetch an oras artifact from an OCI registry
        """
        logger.info("Fetching oras {0}".format(url))
        self.oras("pull", url + ":latest", "--output", os.path.dirname(save_file))
        return save_file

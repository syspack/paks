__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import spack.spec
import paks.repo


class Spec(spack.spec.Spec):
    @property
    def package(self):
        """
        Return a custom repository that can deliver Paks packages
        """
        if not self._package:
            self._package = paks.repo.get(self)
        return self._package

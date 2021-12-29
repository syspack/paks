__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import sys
from .terminal import get_installdir


def add_paks_spack_repo():
    import IPython

    IPython.embed()
    import spack.repo

    spack.repo.add()


def add_spack_to_path():
    """
    Find spack and add to path, allowing for import of spack modules
    """
    # Path to spack install
    spack_prefix = os.path.join(get_installdir(), "spack")
    spack_lib_path = os.path.join(spack_prefix, "lib", "spack")
    spack_external_libs = os.path.join(spack_lib_path, "external")
    for path in [spack_lib_path, spack_external_libs]:
        sys.path.insert(0, path)

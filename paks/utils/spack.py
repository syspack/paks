__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import sys
from .terminal import get_installdir, which, run_command


def add_paks_spack_repo():
    import IPython

    IPython.embed()
    import spack.repo

    spack.repo.add()


def install_spack(repo=None, branch=None):
    """
    Install spack to paks/spack (note this is not used).
    """
    repo = repo or "https://github.com/spack/spack"
    branch = branch or "develop"
    spack_prefix = os.path.join(get_installdir(), "spack")
    return run_command(["git", "clone", "-b", branch, repo, spack_prefix])


def add_spack_to_path():
    """
    Find spack and add to path, allowing for import of spack modules
    """
    # First check for spack in environment
    spack_prefix = which("spack")["message"]
    if spack_prefix:

        # spack -> bin -> root
        spack_prefix = os.path.dirname(os.path.dirname(spack_prefix))

    else:
        # Then check for spack installed to package
        spack_prefix = os.path.join(get_installdir(), "spack")

    # Otherwise, fail
    if not os.path.exists(spack_prefix):
        sys.exit("spack must be installed! Add to path for paks to find.")

    spack_lib_path = os.path.join(spack_prefix, "lib", "spack")
    spack_external_libs = os.path.join(spack_lib_path, "external")
    for path in [spack_lib_path, spack_external_libs]:
        sys.path.insert(0, path)

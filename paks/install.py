__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os

import paks.oras
import paks.sbom
import paks.utils
import paks.defaults


def do_install(self, **kwargs):
    """
    Refactored install process to add proper cache handling.
    """
    from spack.installer import PackageInstaller

    dev_path_var = self.spec.variants.get("dev_path", None)

    if dev_path_var:
        kwargs["keep_stage"] = True

    builder = PackageInstaller([(self, kwargs)])

    # Download what we can find from the GitHub cache
    builder.install()

    # If successful, generate an sbom
    meta_dir = os.path.join(self.prefix, ".spack")
    if os.path.exists(meta_dir):
        sbom = paks.sbom.generate_sbom(self.spec)
        sbom_file = os.path.join(meta_dir, "sbom.json")
        paks.utils.write_json(sbom, sbom_file)

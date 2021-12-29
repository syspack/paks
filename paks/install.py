__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import paks.sbom
import paks.utils
import paks.handlers.github

def do_install(self, **kwargs):
    """
    Refactored install process to add proper cache handling.
    """
    from spack.installer import PackageInstaller

    dev_path_var = self.spec.variants.get("dev_path", None)
    if dev_path_var:
        kwargs["keep_stage"] = True

    # Monkeypatch package installer (not able to import)
    class PakInstaller(PackageInstaller):
        def prepare_cache(self):
            """
            Given that we have a build cache for a package, it includes deps
            """
            # Get trusted GitHub packages in advance 
            gh = paks.handlers.github.GitHub()

            # TODO this requires token with package;read scope
            # https://docs.github.com/en/rest/reference/packages#list-packages-for-an-organization
            for request in self.build_requests:

                # TODO we can get arch here, this can be used to download to cache
                # we will want to match this to container bases available
                # and possibly an abstract one that we can use in scratch
                print(request.pkg.spec.architecture)

    builder = PakInstaller([(self, kwargs)])

    # Download what we can find from the GitHub cache
    builder.prepare_cache()
    builder.install()

    # If successful, generate an sbom
    meta_dir = os.path.join(self.prefix, ".spack")
    if os.path.exists(meta_dir):
        sbom = paks.sbom.generate_sbom(self.spec)
        sbom_file = os.path.join(meta_dir, "sbom.json")
        paks.utils.write_json(sbom, sbom_file)

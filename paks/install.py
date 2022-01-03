__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import re
import shutil
from contextlib import closing
import tarfile

import paks.oras
import paks.sbom
import paks.utils
import paks.defaults
import paks.logger as logger

import spack.binary_distribution as bd
import spack.hooks
import spack.store
import spack.util.crypto
import spack.config
import spack.util.gpg


def verify_tarball(spec_dict, archive):
    """
    Given an spec_json and a tarball, verify that the checksum matches
    """
    spec_json = archive.replace(".spack", ".spec.json")
    signature = "%s.asc" % spec_json
    if not os.path.exists(signature):
        logger.error("Signature does not exist to verify tarball")
        return False

    # Step 1: Verify the signature
    try:
        suppress = spack.config.get("config:suppress_gpg_warnings", False)
        spack.util.gpg.verify(signature, spec_json, suppress)
    except Exception as e:
        logger.error("Signature validation failed")
        return False

    # Step 2: Verify the checksum of the tarball
    checksum = bd.checksum_tarball(targz)
    found_checksum = spec_dict.get("binary_cache_checksum", "").get("hash")
    if found_checksum != checksum:
        logger.error("Checksum %s does not match %s" % ())
        return False
    return True


def get_relative_prefix(prefix, spec_dict):
    """
    Given a spec json, return the buildinfo relative prefix
    """
    new_relative_prefix = str(os.path.relpath(prefix, spack.store.layout.root))

    # if the original relative prefix is in the spec file use it
    buildinfo = spec_dict.get("buildinfo", {})
    return buildinfo.get("relative_prefix", new_relative_prefix)


def stage_package(prefix, targz, spec_dict):
    """
    Given a tar.gz from tmp, extract alongside root, return True on success
    """
    rel_prefix = get_relative_prefix(prefix, spec_dict)

    # Extract alongside so it is likely to be the same filesystem
    stage_dir = os.path.join(spack.store.layout.root, ".tmp")
    paks.utils.mkdirp(stage_dir)
    extract_dir = os.path.join(stage_dir, os.path.basename(rel_prefix))

    # extract the .tar.gz somewhere to get the needed prefix
    with closing(tarfile.open(targz, "r")) as tar:
        tar.extractall(stage_dir)

    # The package folder must have been extracted!
    if not os.path.exists(extract_dir):
        return False

    # Move into correct location
    try:
        shutil.move(extract_dir, prefix)
    except Exception as e:
        shutil.rmtree(extract_dir)
        return False
    return True


def extract_tarball(filename, allow_root=False, unsigned=False):
    """
    extract binary tarball for given package into install area.

    This is different from spack.binary_distribution.extract_tarball because
    the archive name provided is exactly what we use for the tarfile path,
    and we do not always expect it to match a spec.
    """
    # Extract to same directory tarball in - we first extract .spack then .tar.gz
    extract_dir = os.path.dirname(filename)
    with closing(tarfile.open(filename, "r")) as tar:
        tar.extractall(extract_dir)

    # Note that spack also supports .tar.bz2, but we are using .tar.gz
    targz = filename.replace(".spack", ".tar.gz")
    spec_json = filename.replace(".spack", ".spec.json")

    # Cleanup function, for any error that triggers
    def cleanup(msg):
        shutil.rmtree(extract_dir)
        logger.exit(msg)

    if not os.path.exists(spec_json) or not os.path.exists(targz):
        cleanup("%s or %s does not exist in archive." % (spec_json, targz))

    # Note that the loaded spec is hugely missing information
    spec_dict = paks.utils.read_json(spec_json)
    spec = paks.spec.Spec.from_dict(spec_dict)

    # If the spec already exists, it's already extracted
    if os.path.exists(spec.prefix):
        logger.warning("%s already exists, no need to install again." % spec.prefix)

    # verify tarball checksum using the spec json
    if not unsigned and not verify_tarball(spec_dict, targz):
        cleanup("Cannot verify %s" % targz)

    # prepare package to relocate by extracting to .tmp in root
    if not stage_package(spec.prefix, targz, spec_dict):
        cleanup("Failed to stage package")

    try:
        bd.relocate_package(spec, allow_root)
    except Exception as e:
        cleanup("Failed to relocate package.")

    # Do we care if there isn't a manifest file here?
    # Final cleanup!
    shutil.rmtree(extract_dir)


def do_install(self, **kwargs):
    """
    Refactored install process to add proper cache handling.
    """
    from spack.installer import PackageInstaller

    dev_path_var = self.spec.variants.get("dev_path", None)
    registries = kwargs.get("registries")
    tag = kwargs.get("tag")

    if dev_path_var:
        kwargs["keep_stage"] = True

    class PakInstaller(PackageInstaller):
        """
        The PakInstaller wraps the PackageInstaller.

        We take this inline approach because we are not able to import it.
        """

        def prepare_cache(self, registries=None, tag=None):
            """
            Given that we have a build cache for a package, install it.

            Since the GitHub packages API requires a token, we take an approach
            that attempts a pull for an artifact, and just continue if we don't
            have one.
            """
            # If no registries in user settings or command line, use default
            if not registries:
                registries = [paks.defaults.trusted_packages_registry]
            tag = tag or paks.defaults.default_tag

            # prepare oras client
            oras = paks.oras.Oras()

            # If we want to use Github packages API, it requires token with package;read scope
            # https://docs.github.com/en/rest/reference/packages#list-packages-for-an-organization
            for request in self.build_requests:

                # Don't continue if installed!
                if request.spec.install_status() == True:
                    continue

                # The name of the expected package, and directory to put it
                name = bd.tarball_name(request.pkg.spec, ".spack")
                tmpdir = paks.utils.get_tmpdir()

                # Try until we get a cache hit
                cache_hit = False
                for registry in registries:
                    uri = "%s/%s:%s" % (registry, name, tag)

                    # Retrieve the artifact (will be None if doesn't exist)
                    artifact = oras.fetch(uri, os.path.join(tmpdir, name))
                    if artifact:
                        cache_hit = True
                        break

                # Don't continue if not found
                if not cache_hit:
                    shutil.rmtree(tmpdir)
                    continue

                # Checksum check (removes sha256 prefix)
                sha256 = oras.get_manifest_digest(uri)
                if sha256:
                    checker = spack.util.crypto.Checker(sha256)
                    if not checker.check(artifact):
                        logger.exit("Checksum of %s is not correct." % artifact)

                # TODO: we need to push a binary that doensn't have a hash
                # then we need to do this same extraction (to the correct directory)
                # and then make sure install runs with reuse
                # If we have an artifact, extract where needed and tell spack it's installed!
                if artifact:

                    # Note - for now not signing, since we don't have a consistent key strategy
                    extract_tarball(artifact, unsigned=True)
                    spack.hooks.post_install(request.pkg.spec)
                    spack.store.db.add(request.pkg.spec, spack.store.layout)

    builder = PakInstaller([(self, kwargs)])

    # Download what we can find from the GitHub cache
    builder.prepare_cache(registries, tag)
    builder.install()

    # If successful, generate an sbom
    meta_dir = os.path.join(self.prefix, ".spack")
    if os.path.exists(meta_dir):
        sbom = paks.sbom.generate_sbom(self.spec)
        sbom_file = os.path.join(meta_dir, "sbom.json")
        paks.utils.write_json(sbom, sbom_file)

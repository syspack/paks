__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
import paks.utils as utils
from spack.main import SpackCommand
import paks.defaults
import paks.oras
import os

gpg = SpackCommand("gpg")
bc = SpackCommand("buildcache")


def gpg_init(dirname):
    """
    Init the gpg directory, setting permissions etc.
    """
    utils.mkdirp(dirname)
    os.chmod(dirname, 0o700)


def get_gpg_key():
    """
    Find the first key created for spack

    This would really be nicer if we didn't have to use gpg :)
    """
    key = None
    lines = gpg("list").split("\n")
    for i, line in enumerate(lines):
        if "Spack" in line:
            key = lines[i - 1].strip()
            break
    return key


class BuildCache:
    """
    A controller that makes it easy to create a build cache and install to it.
    """

    def __init__(self, cache_dir=None, username=None, email=None):
        if not cache_dir:
            cache_dir = utils.get_tmpdir()
        self.cache_dir = cache_dir

        # Use defautls for username and email if not provided
        username = username or utils.get_username()
        email = email or "%s@users.noreply.spack.io" % username

        # TODO eventually we want to store keys elsewhere (this doesn't seem to work)
        # self.keys_home = paks.defaults.keys_dir
        # if not os.path.exists(self.keys_home):
        #    gpg_init(self.keys_home)

        # Set the home to a non-spack location
        # os.putenv('SPACK_GNUPGHOME', self.keys_home)
        # os.environ['SPACK_GNUPGHOME'] = self.keys_home

        # Ensure we have the gpg keys init, etc.
        # gpg("init", "--from", self.keys_home)

        gpg("init")
        gpg("create", username, email)

    def create(self, specs, key=None):
        """
        Create the build cache with some number of specs

        Ideally we could do spack buildcache add but that isn't supported.
        """
        # If a key isn't defined, choose the first spack one we find
        if not key:
            key = get_gpg_key()
        format_string = " ".join(["%s@%s" % (s.name, s.version) for s in specs])
        if key:
            print(
                bc("create", "-r", "-a", "-k", key, "-d", self.cache_dir, format_string)
            )
        else:
            print(bc("create", "-r", "-a", "-d", self.cache_dir, format_string))

    def push(self, uri):
        """
        Push the build cache to an OCI registry (compatible with ORAS)
        """
        # Find all .spack archives in the cache
        for archive in utils.recursive_find(self.cache_dir, ".spack"):
            package_name = os.path.basename(archive)
            print(package_name)
            # TODO Absolute paths not allowed
            # mv ${spack_package} ${spack_package_name}
            # package_full_name=ghcr.io/${GITHUB_REPOSITORY}/${package_name}:latest
            # package_tagged_name=ghcr.io/${GITHUB_REPOSITORY}/${package_name}:${INPUT_TAG}
            # oras push ${package_full_name} --manifest-config /dev/null:${package_content_type} ${spack_package_name}
            # TODO how to add sbom? separately?
            # TODO we should support custom tags

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[paks-build-cache]"

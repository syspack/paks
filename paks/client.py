__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
import paks.cache
from .settings import Settings

import spack.cmd
import spack.target
import spack.main
import spack.config

import json

import paks.spec


class PakClient:
    """
    Paks has a main controller for interacting with paks.
    """

    def __init__(self, *args, **kwargs):
        settings_file = kwargs.get("settings_file")
        validate = kwargs.get("validate", True)
        if not hasattr(self, "settings"):
            self.settings = Settings(settings_file, validate=validate)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[paks-client]"

    def iter_specs(self, packages, registries=None, use_cache=False):
        """
        A shared function to retrieve iterable of specs from packages
        """
        for spec in paks.spec.parse_specs(packages, registries, use_cache):
            yield spec

    def list_installed(self):
        """
        List installed packages
        """
        find = spack.main.SpackCommand("find")
        print(find())
        return json.loads(find("--json"))

    def build(self, packages, cache_dir=None, key=None, registry=None, tag=None):
        """
        Build a package into a cache
        """
        # Prepare a cache directory
        cache = paks.cache.BuildCache(
            cache_dir=cache_dir or self.settings.cache_dir,
            username=self.settings.username,
            email=self.settings.email,
            settings=self.settings,
        )

        if not registry:
            registry = paks.defaults.trusted_packages_registry

        # Install all packages, and also generate sboms
        specs = self.install(packages, registry=registry, tag=tag)

        # TODO how can we attach the sbom to the package (aside from being in archive?)
        cache.create(specs, key=key)
        return cache

    def push(self, uri, cache_dir=None, tag=None):
        """
        Given an existing cache directory, push known specs to a specific uri
        """
        # Prepare a cache directory
        cache = paks.cache.BuildCache(
            cache_dir=cache_dir or self.settings.cache_dir,
            username=self.settings.username,
            email=self.settings.email,
            settings=self.settings,
        )
        cache.push(uri, tag=tag)
        return cache

    def add_repository(self, path):
        """
        Add a repository.

        Given a path that exists, add the repository to the
        underlying spack. If you need to add a GitHub uri, create a
        paks.repo.PakRepo first.
        """
        repos = spack.config.get("repos")
        repos.insert(0, path)
        spack.config.set("repos", repos)

    def install(self, packages, registry=None, tag=None, use_cache=True):
        """
        Install one or more packages.

        This eventually needs to take into account using the GitHub packages bulid cache
        """
        # Default to registries defined in settings
        registries = self.settings.trusted_pull_registries

        # Do we have an additional trusted registry provided on the command line?
        if registry:
            registries = [registry] + registries

        specs = []
        for spec in self.iter_specs(packages, registries, use_cache=use_cache):
            logger.info("Preparing to install %s" % spec.name)
            spec.package.do_install(force=True, tag=tag or self.settings.default_tag)
            specs.append(spec)
        return specs

    def uninstall(self, packages):
        """
        Uninstall a spack package
        """
        for spec in self.iter_specs(packages):
            try:
                spec.package.do_uninstall(force=True)
            except Exception as ex:
                logger.exit(ex)

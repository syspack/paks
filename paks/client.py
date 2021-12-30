__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
import paks.cache
import paks.utils as utils
from .settings import Settings

import spack.cmd
import spack.target
import spack.main

import os
import json
import re
import shutil
import sys

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

    def iter_specs(self, packages, concretize=True):
        """
        A shared function to retrieve iterable of specs from packages
        """
        for spec in paks.spec.parse_specs(packages):
            yield spec

    def list_installed(self):
        """
        List installed packages
        """
        find = spack.main.SpackCommand("find")
        print(find())
        return json.loads(find("--json"))

    def build(self, packages, cache_dir=None, key=None):
        """
        Build a package into a cache
        """
        # Prepare a cache directory
        cache = paks.cache.BuildCache(
            cache_dir=cache_dir,
            username=self.settings.username,
            email=self.settings.email,
            settings=self.settings,
        )

        # Install all packages, and also generate sboms
        specs = self.install(packages)

        # TODO how can we attach the sbom to the package (aside from being in archive?)
        cache.create(specs, key=key)
        return cache

    def push(self, cache_dir, uri):
        """
        Given an existing cache directory, push known specs to a specific uri
        """
        # Prepare a cache directory
        cache = paks.cache.BuildCache(
            cache_dir=cache_dir,
            username=self.settings.username,
            email=self.settings.email,
            settings=self.settings,
        )
        cache.push(uri)
        return cache

    def install(self, packages):
        """
        Install one or more packages.

        This eventually needs to take into account using the GitHub packages bulid cache
        """
        specs = []
        for spec in self.iter_specs(packages):
            logger.info("Preparing to install %s" % spec.name)

            # TODO here we actually want to insert preparing GitHub packages build cache
            # We should match based on a basic set of architectures we know the containers support
            # E.g., check the platform and spit an error if it's some niche HPC one.

            spec.package.do_install(
                force=True,
                trusted_registry=self.settings.trusted_packages_registry,
                tag=self.settings.default_tag,
            )
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

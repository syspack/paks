__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"


import paks.repo
import paks.oras
import paks.defaults

import spack.spec
import spack.util.string

import six


class Spec(spack.spec.Spec):
    @property
    def package(self):
        """
        Return a custom repository that can deliver Paks packages
        """
        if not self._package:
            self._package = paks.repo.get(self)
        return self._package


def wrap_spec(legacy, set_arch=True):
    """
    Get a Paks spec (with the general arch) from a spack legacy spec.
    """
    # Create a new Pak spec to copy (duplicate) into
    spec = Spec()
    spec._dup(legacy)

    # Always set the arch to be general
    if set_arch:
        spec.architecture = spack.spec.ArchSpec()
        spec.architecture.target = spack.target.Target("x86_64")
    return spec


def parse_specs(packages, registries=None):
    """Parse specs from a list of strings, and concretize"""
    if not isinstance(packages, six.string_types):
        packages = " ".join(spack.util.string.quote(packages))

    specs = []
    for legacy in spack.spec.SpecParser().parse(packages):
        spec = wrap_spec(legacy)

        # Prepare the spec cache before concretize
        paks.cache.prepare_cache(spec, registries)
        spec.concretize(reuse=True)
        specs.append(spec)
    return specs

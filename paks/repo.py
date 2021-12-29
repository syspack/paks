__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import paks.install
import spack.repo
import llnl.util.lang
import spack.util.naming as nm

import six
import sys
import os


class RepoPath(spack.repo.RepoPath):
    def __init__(self, *repos):
        """
        Since we want control over customizing the package class, we return
        a paks.repo.Repo instead.
        """
        self.repos = []
        self.by_namespace = nm.NamespaceTrie()

        self._provider_index = None
        self._patch_index = None
        self._tag_index = None

        # Add each repo to this path.
        for repo in repos:
            try:
                if isinstance(repo, six.string_types):
                    repo = Repo(repo)
                self.put_last(repo)
            except spack.repo.RepoError as e:
                tty.warn(
                    "Failed to initialize repository: '%s'." % repo,
                    e.message,
                    "To remove the bad repository, run this command:",
                    "    spack repo rm %s" % repo,
                )


class Repo(spack.repo.Repo):
    @spack.repo.autospec
    def get_remote(self, spec):
        """
        TODO we will want to be able to retrieve a package via a GitHub URI
        """
        # TODO need to add design for a remote repo to install from

        # Given github repository, clone
        # package name should be repository namespace
        # look for package.py
        # Throw into "on the fly" repo under same namespace
        # return spec
        pass

    @spack.repo.autospec
    def get(self, spec):
        """Returns the package associated with the supplied spec

        However we add custom functions provided by Paks.
        """
        if spec.name is None:
            raise spack.repo.UnknownPackageError(None, self)

        if spec.namespace and spec.namespace != self.namespace:
            raise spack.repo.UnknownPackageError(spec.name, self.namespace)

        package_class = self.get_pkg_class(spec.name)

        # Monkey patch the class with the new install!
        package_class.do_install = paks.install.do_install

        try:
            return package_class(spec)
        except spack.error.SpackError:
            # pass these through as their error messages will be fine.
            raise
        except Exception as e:
            tty.debug(e)

            # Make sure other errors in constructors hit the error
            # handler by wrapping them
            if spack.config.get("config:debug"):
                sys.excepthook(*sys.exc_info())
            raise spack.repo.FailedConstructorError(spec.fullname, *sys.exc_info())


def _singleton_path(repo_dirs=None):
    """
    Get a singleton repository path, along with paks custom
    """
    repo_dirs = repo_dirs or spack.config.get("repos")
    if not repo_dirs:
        raise NoRepoConfiguredError(
            "Spack configuration contains no package repositories."
        )

    path = RepoPath(*repo_dirs)
    sys.meta_path.append(path)
    return path


#: Singleton repo path instance
path = llnl.util.lang.Singleton(_singleton_path)


def get(spec):
    """Convenience wrapper around ``spack.repo.get()``."""
    # TODO add support here for a spec name that is from GitHub
    # And then add to singleton path (do dynamically as function)
    return path.get(spec)

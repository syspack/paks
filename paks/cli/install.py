__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.client import PakClient
from paks.repo import PakRepo

import re
import os


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)

    # By defualt, assume not adding a repository
    repo = None

    # Case 1: we have an install directed at the present working directory
    if args.packages and args.packages[0] == ".":
        repo = os.getcwd()
        args.packages.pop(0)

    # If we have a path (akin to the first)
    if args.packages and os.path.exists(args.packages[0]):
        repo = args.packages.pop(0)

    # OR if we have a github URI
    if args.packages and re.search("(http|https)://github.com", args.packages[0]):
        repo = args.packages.pop(0)

    # Add the repository
    repo = PakRepo(repo)

    # If we don't have packages and we have a repo, derive from PWD
    if not args.packages:
        args.packages = repo.list_packages()

    # Finally, add the repository and install packages
    cli.add_repository(repo.repo_dir)
    cli.install(args.packages)

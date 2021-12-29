__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.client import PakClient


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)
    cache = cli.build(args.packages, args.cache_dir, args.key)

    # Do we want to push to a build cache?
    if args.push:
        cache.push(args.push)

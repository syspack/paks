__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.client import PakClient
from paks.logger import logger


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)
    cache = cli.build(args.packages, args.cache_dir, args.key)

    # We cannot have both
    if args.push and args.push_trusted:
        logger.exit("Please use only --push or --pushd")

    # Do we want to push to a build cache?
    if args.push or args.push_trusted:
        cache.push(args.push)

        # By default, we clean up the build cache
        if not args.no_cleanup:
            cache.remove()

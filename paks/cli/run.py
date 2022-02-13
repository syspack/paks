__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.client import PakClient
from paks.logger import logger


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)

    # Update settings
    for s in args.s or []:
        if "=" not in s:
            logger.warning("Malformed setting %s: skipping." % s)
            continue
        key, value = s.split("=", 1)
        cli.settings.add(key, value)

    # Run the container!
    cli.run(
        args.image,
        registry=args.registry,
        shell=args.shell,
        container_tech=args.container_tech,
    )

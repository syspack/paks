__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.client import PakClient
from paks.logger import logger
import sys


def main(args, parser, extra, subparser):
    """
    paks env edit <env-name>
    paks env add name=value <env-name>
    paks env remove name <env-name>
    paks env rm name <env-name>
    """
    # If nothing provided, show help
    if not args.params:
        print(subparser.format_help())
        sys.exit(0)

    # We are required a command and env name (minimally)
    if len(args.params) < 2:
        print(subparser.format_help())
        sys.exit(0)

    # The first "param" is either add, rm/remove, or edit
    command = args.params.pop(0)
    envname = args.params.pop(0)

    validate = True if not command == "edit" else False
    cli = PakClient(settings_file=args.settings_file, validate=validate)

    # For each new setting, update and save!
    if command == "edit":
        return cli.env.edit(envname)
    elif command == "show":
        content = cli.env.show(envname)
        print(content)
    elif command in ["rm", "remove"]:
        varname = envname
        if not args.params:
            logger.exit("Missing environment name at end.")
        envname = args.params.pop(0)
        cli.env.remove(envname, varname)
    elif command in ["add"]:
        keyval = envname
        if not args.params:
            logger.exit("Missing environment name at end.")
        envname = args.params.pop(0)
        cli.env.add(envname, keyval, force=args.force)
    else:
        logger.error("%s is not a recognized command." % command)

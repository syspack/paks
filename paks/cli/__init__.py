#!/usr/bin/env python

__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import paks
from paks.logger import setup_logger
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(
        description="paks interactive container commands",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--settings-file",
        dest="settings_file",
        help="custom path to settings file.",
    )
    subparsers = parser.add_subparsers(
        help="actions",
        title="actions",
        description="actions",
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", description="show software version")

    run = subparsers.add_parser(
        "run",
        description="run an interactive container",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    run.add_argument(
        "--shell",
        "--sh",
        dest="shell",
        help="Use a one-off shell instead of the one defined in your config.",
    )
    run.add_argument(
        "-s", action="append", help="key=value argument to update settings."
    )

    # Paks environments
    env = subparsers.add_parser(
        "env",
        description="interact with paks environments",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    env.add_argument(
        "params",
        nargs="*",
        help="""interact with named environments written to ~/.paks/envs
paks env edit <env-name>
paks env add name=value <env-name>
paks env remove name <env-name>
paks env rm name <env-name>
""",
    )
    env.add_argument(
        "--force",
        dest="force",
        help="force replacement if environemnt variable already exists (for add)",
        default=False,
        action="store_true",
    )

    config = subparsers.add_parser(
        "config",
        description="update configuration settings. Use set or get to see or set information.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    config.add_argument(
        "--central",
        "-c",
        dest="central",
        help="make edits to the central config file, if a user config is default.",
        default=False,
        action="store_true",
    )

    config.add_argument(
        "params",
        nargs="*",
        help="""Set or get a config value, edit the config, add or remove a list variable, or create a user-specific config.
paks config set key:value
paks config get key
paks edit
paks config init""",
        type=str,
    )

    for command in [run]:
        command.add_argument("image", help="image to run")

    for command in [run]:
        command.add_argument(
            "--registry",
            "-r",
            dest="registry",
            help="registry to use, if required for command.",
        )
        command.add_argument(
            "--container-tech",
            "-c",
            dest="container_tech",
            help="container technology to use, to over-ride user settings.",
        )

    return parser


def run_main():
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """

        version = paks.__version__

        print("\nPaks v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(paks.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    if args.command == "run":
        from .run import main
    elif args.command == "config":
        from .config import main
    elif args.command == "env":
        from .env import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args, parser=parser, extra=extra, subparser=helper)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1
    help(return_code)


if __name__ == "__main__":
    run_main()

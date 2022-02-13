__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import locale
import subprocess
import shlex
import sys
import paks.env
import paks.utils


class Result:
    """
    A Result objet holds output and error, and a return value and message
    """

    def __init__(self, out=None, err=None, retval=0, msg=None):
        self.returncode = retval
        self.out = out or []
        self.err = err or []
        self.message = msg


class Command:
    """Class method to invoke shell commands and retrieve output and error.
    This class is inspired and derived from utils functions in
    https://github.com/vsoch/scif
    """

    # Assume we can support all three
    supported_tech = ["docker", "podman", "singularity"]

    # Message to print before run
    pre_message = None

    # Parse kwargs? (e.g., envars will have=)
    parse_kwargs = True

    def __init__(self, tech, required=None, out=None):
        """
        Backend is required to update history.
        """
        self.tech = tech
        self.required = required or []
        self.failed = False
        self.out = out or sys.stdout.fileno()

        # We don't need editor for interactive commands
        self.env = paks.env.Environment(quiet=True)

        # Don't add commands executed to history
        os.putenv("HISTCONTROL", "ignorespace")
        os.environ["HISTCONTROL"] = "ignorespace"

    def execute(self, cmd):
        """
        Execute a command to the container
        """
        # Extra space prevents saving to history
        os.write(self.out, self.encode(" \r %s" % cmd))

    def execute_get(self, runcmd, getcmd):
        """
        Execute and get runs a command inside the container (pipes to temporary
        file) and then loads from the outside.
        """
        # This is run inside the container
        self.run_hidden(runcmd)
        out, err = self.execute_host(getcmd)
        return out

    def execute_host(self, cmd):
        """
        Execute a command to the host, return out and error
        """
        # This is run outside the container
        res = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        out, err = res.communicate()
        return out, err

    def run_hidden(self, cmd):
        """
        Run a hidden command.
        """
        # TODO how to hide this?
        os.write(self.out, self.encode(" %s\r" % cmd))

    def check(self, **kwargs):
        """
        Check ensures that:

        1. The container tech of the command matches the class
        2. Required arguments are provided.
        """
        if self.tech not in self.supported_tech:
            return self.return_failure(
                "This command is not specified to run with %s." % self.tech
            )

        # Required args for all commands
        for entry in self.required:
            if entry not in kwargs:
                return self.return_failure("%s is required." % entry)

        args = kwargs.get("original")
        self.kwargs = kwargs

        # Get args (parsing from the original command line)
        parsed_args = []
        if args:
            parsed_args, kwargs = self.get_args(args)
            self.kwargs.update(kwargs)
        self.args = parsed_args

    def get_args(self, cmd):
        """
        Once we get here, we only care about additional command args.
        """
        parts = cmd.split(" ")

        # Pop off the command (we already use it)
        parts.pop(0).strip()
        kwargs = {}
        args = []
        for arg in parts:

            # This is an arg
            if "=" not in arg:
                arg = arg.strip()

                # Don't append empty args
                if not arg:
                    continue
                args.append(arg)
                continue

            # This is a kwarg
            if self.parse_kwargs:
                key, val = arg.split("=", 1)
                kwargs[key.strip()] = val.strip()

            # A command can choose to not split/parse
            else:
                args.append(arg.strip())
        return args, kwargs

    def return_failure(self, message, out=None, err=None):
        """
        Return a failed result (requires a message)
        """
        return Result(msg=message, retval=1, out=out, err=err)

    def return_success(self, message=None, out=None, err=None):
        """
        Return a successful result
        """
        return Result(msg=message, retval=0, out=None, err=None)

    def do_print(self, line, clear=True):
        if clear:
            print("\r")
        print(line, end="\r")

    def run_command(self, cmd, output="output"):
        """
        Wrapper to stream a command, which handles returning a result on error.
        """
        print("\r")
        lines = self.stream_command(cmd, output)
        while True:
            try:
                line = next(lines)
                self.do_print(line, False)

            # We use this to return the result
            except StopIteration as e:
                return e.value
                break

    def stream_command(self, cmd, output="output"):
        """
        Stream a command and use output or error.
        """
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        stream = process.stdout.readline
        if output == "error":
            stream = process.stderr.readline

        # Stream lines back to the caller
        for line in iter(stream, ""):
            yield line

        # If there is an error, raise.
        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()

        # If failed, send failed result up to calling function
        if return_code:
            return self.return_failure("Failed: %s" % " ".join(cmd))

    def parse_command(self, cmd):
        """this is called when a new command is provided to ensure we have
        a list. We don't check that the executable is on the path,
        as the initialization might not occur in the runtime environment.
        """
        if not isinstance(cmd, list):
            cmd = shlex.split(cmd)
        return cmd

    def encode(self, line):
        return bytes(line.encode("utf-8"))

    def decode(self, line):
        """Given a line of output (error or regular) decode using the
        system default, if appropriate
        """
        loc = locale.getdefaultlocale()[1]

        try:
            line = line.decode(loc)
        except:
            pass
        return line

__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import locale
import subprocess
import shlex
import shutil
import tempfile
import paks.utils


class Capturing:
    """capture output from stdout and stderr into capture object.
    This is based off of github.com/vsoch/gridtest but modified
    to write files. The stderr and stdout are set to temporary files at
    the init of the capture, and then they are closed when we exit. This
    means expected usage looks like:

    with Capturing() as capture:
        process = subprocess.Popen(...)

    And then the output and error are retrieved from reading the files:
    and exposed as properties to the client:

        capture.out
        capture.err

    And cleanup means deleting these files, if they exist.
    """

    def __enter__(self):
        self.set_stdout()
        self.set_stderr()
        return self

    def set_stdout(self):
        self.stdout = open(tempfile.mkstemp()[1], "w")

    def set_stderr(self):
        self.stderr = open(tempfile.mkstemp()[1], "w")

    def __exit__(self, *args):
        self.stderr.close()
        self.stdout.close()

    @property
    def out(self):
        """Return output stream. Returns empty string if empty or doesn't exist.
        Returns (str) : output stream written to file
        """
        if os.path.exists(self.stdout.name):
            return paks.utils.read_file(self.stdout.name)
        return ""

    @property
    def err(self):
        """Return error stream. Returns empty string if empty or doesn't exist.
        Returns (str) : error stream written to file
        """
        if os.path.exists(self.stderr.name):
            return paks.utils.read_file(self.stderr.name)
        return ""

    def cleanup(self):
        for filename in [self.stdout.name, self.stderr.name]:
            if os.path.exists(filename):
                os.remove(filename)


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

    def __init__(self, tech, required=None):
        self.tech = tech
        self.required = required or []

    def check(self, **kwargs):
        """
        Check ensures that:

        1. The container tech of the command matches the class
        2. Required arguments are provided.
        """
        if self.tech not in self.supported_tech:
            return self.return_failure(
                "This command is not specified to run with %s." % tech
            )

        # Required args for all commands
        for entry in self.required:
            if entry not in kwargs:
                return self.failed_result("%s is required." % entry)

        args = kwargs.get("original")
        self.kwargs = kwargs

        # Get args (parsing from the original command line)
        if args:
            self.kwargs.update(self.get_args(args))

    def get_args(self, cmd):
        """
        Once we get here, we only care about additional command args.
        """
        parts = cmd.split(" ")

        # Pop off the command (we already use it)
        parts.pop(0).strip()
        args = {}
        for arg in parts:
            if "=" not in arg:
                continue
            key, val = art.split("=", 1)
            args[key.strip()] = val.strip()
        return args

    def return_failure(self, message, out=None, err=None):
        """
        Return a failed result.
        """
        return Result(msg=message, retval=1, out=out, err=err)

    def return_success(self, message, out=None, err=None):
        """
        Return a successful result
        """
        return Result(msg=message, retval=0, out=None, err=None)

    def parse_command(self, cmd):
        """this is called when a new command is provided to ensure we have
        a list. We don't check that the executable is on the path,
        as the initialization might not occur in the runtime environment.
        """
        if not isinstance(cmd, list):
            cmd = shlex.split(cmd)
        return cmd

    def execute(self, cmd, args=None, do_capture=False):
        """Execute a system command and return a result"""
        cmd = self.parse_command(cmd)
        if args:
            cmd = cmd + self.parse_command(args)

        # Reset the output and error records
        result = Result()

        # The executable must be found, return code 1 if not
        executable = shutil.which(cmd[0])
        if not executable:
            result.err = ["%s not found." % cmd[0]]
            result.returncode = 1
            return result

        # remove the original executable
        args = cmd[1:]

        # Use updated command with executable and remainder (list)
        cmd = [executable] + args

        # Capturing provides temporary output and error files
        if do_capture:
            with Capturing() as capture:
                process = subprocess.Popen(
                    cmd,
                    stdout=capture.stdout,
                    stderr=capture.stderr,
                    universal_newlines=True,
                )
                returncode = process.poll()

                # Iterate through the output
                while returncode is None:
                    returncode = process.poll()

            # Get the remainder of lines, add return code
            result.out += ["%s\n" % x for x in self.decode(capture.out) if x]
            result.err += ["%s\n" % x for x in self.decode(capture.err) if x]

            # Cleanup capture files and save final return code
            capture.cleanup()
        else:
            res = paks.utils.run_command(cmd)
            returncode = res["return_code"]
            result.message = res["message"]

        result.returncode = returncode
        return result

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

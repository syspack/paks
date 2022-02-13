__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.utils.names import namer
from paks.logger import logger
import paks.utils
import paks.defaults
import paks.templates
import paks.commands
import paks.settings

import subprocess
import select
import string
import pty
import termios
import tty
import os
import sys
import re


class ContainerName:
    """
    Parse a container name into named parts
    """

    def __init__(self, raw):
        self.raw = raw
        self.registry = None
        self.repository = None
        self.tool = None
        self.version = None
        self.digest = None
        self.parse(raw)
        self._name = None

    @property
    def extended_name(self):
        if not self._name:
            self._name = namer.generate()
        return self.slug + "-" + self._name

    @property
    def name(self):
        if not self._name:
            self._name = namer.generate()
        return self._name

    @property
    def slug(self):
        slug = ""
        for attr in [self.registry, self.repository, self.tool, self.version]:
            if attr and not slug:
                slug = attr.replace(".", "")
            elif attr and slug:
                slug = slug + "-" + attr.replace(".", "")
        return slug

    def parse(self, raw):
        """
        Parse a name into known pieces
        """
        match = re.search(paks.templates.docker_regex, raw)
        if not match:
            logger.exit("%s does not match a known identifier pattern." % raw)
        for key, value in match.groupdict().items():
            value = value.strip("/") if value else None
            setattr(self, key, value)


class ContainerTechnology:
    """
    A base class for a container technology
    """

    def __init__(self, settings=None):
        if not settings:
            settings = paks.settings.Settings(paks.defaults.settings_file)
        self.settings = settings

    def get_history(self, line, openpty):
        """
        Given an input with some number of up/down and newline, derive command.
        """
        up = line.count("[A")
        down = line.count("[B")
        change = up - down

        # pushed down below history
        if change <= 0:
            return ""
        history = self.hist.run(
            container_name=self.uri.extended_name,
            out=openpty,
            history_file=self.settings.history_file,
            user=self.settings.user,
        )
        history = [x for x in history.split("\n") if x]

        if not history:
            return ""

        if change > len(history):
            return ""

        # here we are looking back up into history (negative index)
        newline = history[-1 * change]

        # Add back any characters typed
        newline += re.split("(\[A|\[B)", line, 1)[-1]
        return newline

    def encode(self, msg):
        return bytes((msg).encode("utf-8"))

    def interactive_command(self, cmd):
        """
        Ensure we always restore original TTY otherwise terminal gets messed up
        """
        # Controller to get history
        self.hist = self.commands.history

        # save original tty setting then set it to raw mode
        old_tty = termios.tcgetattr(sys.stdin)
        old_pty = termios.tcgetattr(sys.stdout)
        try:
            self._interactive_command(cmd)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
            termios.tcsetattr(sys.stdout, termios.TCSADRAIN, old_pty)

    def run_executor(self, string_input, openpty):
        """
        Given a string input, run executor
        """
        string_input = string_input.replace("[A", "").replace("[B", "")
        if not string_input.startswith("#"):
            return

        executor = self.commands.get_executor(string_input, out=openpty)
        if executor is not None:

            # Provide pre-command message to the terminal
            if executor.pre_message:
                print("\n\r" + executor.pre_message)

            # If we have an executor for the command, run it!
            # All commands require the original / current name
            result = executor.run(
                name=self.image,
                container_name=self.uri.extended_name,
                original=string_input,
            )
            if result.message:
                print("\r" + result.message)

    def clean(self, string_input):
        string_input = re.sub(
            r"[^a-zA-Z0-9%s\n\r\w ]" % string.punctuation, "", string_input
        )
        return string_input.replace("\x1b", "")

    def welcome(self, openpty):
        """
        Welcome the user and clear terminal
        """
        # Don't add commands executed to history
        os.write(openpty, self.encode(" export PROMPT_COMMAND='history -a'\r"))
        os.write(openpty, self.encode(" clear\r"))
        os.write(openpty, self.encode(" ### Welcome to PAKS! ###\r"))

    def _interactive_command(self, cmd):
        """
        Run an interactive command.
        """
        tty.setraw(sys.stdin.fileno())

        # open pseudo-terminal to interact with subprocess
        openpty, opentty = pty.openpty()

        # use os.setsid() make it run in a new process group, or bash job control will not be enabled
        p = subprocess.Popen(
            cmd,
            preexec_fn=os.setsid,
            stdin=opentty,
            stdout=opentty,
            stderr=opentty,
            universal_newlines=True,
        )

        # Welcome to Paks!
        self.welcome(openpty)
        string_input = ""

        while p.poll() is None:
            r, w, e = select.select([sys.stdin, openpty], [], [])
            if sys.stdin in r:
                terminal_input = os.read(sys.stdin.fileno(), 10240)
                new_char = terminal_input.decode("utf-8")

                # if we have a backspace (ord 127)
                if len(new_char) == 1 and ord(new_char) == 127:

                    # Backspace to empty line
                    if len(string_input) > 0:
                        string_input = string_input[:-1]
                    if not string_input:
                        os.write(openpty, terminal_input)
                        continue
                else:
                    string_input = string_input + new_char

                # Get rid of left/right
                string_input = string_input.replace("[D", "").replace("[C", "")
                has_newline = "\n" in string_input or "\r" in string_input

                # Replace weird characters and escape sequences
                string_input = self.clean(string_input)

                # Universal exit command
                if "exit" in string_input and has_newline:
                    print("\n\rContainer exited.\n\r")
                    return self.uri.extended_name

                # Pressing up or down, but not enter
                if ("[A" in string_input or "[B" in string_input) and not has_newline:
                    string_input = self.get_history(string_input, openpty)
                    os.write(openpty, terminal_input)
                    continue

                # Pressing up or down with enter
                if ("[A" in string_input or "[B" in string_input) and has_newline:
                    string_input = self.get_history(string_input, openpty)
                    os.write(openpty, terminal_input)

                if not string_input:
                    continue

                # If we have a newline (and possibly a command)
                if has_newline:
                    self.run_executor(string_input, openpty)

                    # Add derived line to the history
                    os.write(openpty, terminal_input)
                    string_input = ""
                else:
                    os.write(openpty, terminal_input)

            elif openpty in r:
                o = os.read(openpty, 10240)
                if o:
                    os.write(sys.stdout.fileno(), o)

    def __str__(self):
        return str(self.__class__.__name__)

__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.utils.names import namer
from paks.logger import logger
import paks.utils
import paks.templates


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

    def __init__(self):

        # Save history for the length of one interactive command (shell)
        self.clear_history()

        # If we weren't created with settings, add empty
        if not hasattr(self, "settings"):
            from paks.settings import EmptySettings

            self.settings = EmptySettings()

    def clear_history(self):
        self.history = []

    def get_history(self, line):
        """
        Given an input with some number of up/down and newline, derive command.
        """
        up = line.count("[A")
        down = line.count("[B")
        change = up - down

        # 0 change - we are on same line
        # here we are looking back up into history (negative index)
        if change > 0 and len(self.history) >= change:
            newline = self.history[-1 * change]
            newline += line.replace("[A", "").replace("[B", "")
            return newline

        # If we get here, either down error or no change
        return ""

    def encode(self, msg):
        return bytes((msg).encode("utf-8"))

    def interactive_command(self, cmd):
        """
        Ensure we always restore original TTY otherwise terminal gets messed up
        """
        # save original tty setting then set it to raw mode
        old_tty = termios.tcgetattr(sys.stdin)
        old_pty = termios.tcgetattr(sys.stdout)
        try:
            self._interactive_command(cmd)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
            termios.tcsetattr(sys.stdout, termios.TCSADRAIN, old_pty)

    def _interactive_command(self, cmd):
        """
        Run an interactive command.
        """
        tty.setraw(sys.stdin.fileno())

        # open pseudo-terminal to interact with subprocess
        openpty, opentty = pty.openpty()

        # The user will likely press up / down, we can store a limited history back
        self.clear_history()

        # use os.setsid() make it run in a new process group, or bash job control will not be enabled
        p = subprocess.Popen(
            cmd,
            preexec_fn=os.setsid,
            stdin=opentty,
            stdout=opentty,
            stderr=opentty,
            universal_newlines=True,
        )

        # Since every poll is for a character, we need to keep adding to
        # the string until we detect a newline (then parse for a command)
        string_input = ""
        while p.poll() is None:
            r, w, e = select.select([sys.stdin, openpty], [], [])
            if sys.stdin in r:
                terminal_input = os.read(sys.stdin.fileno(), 10240)
                new_char = terminal_input.decode("utf-8")

                # if we have a backspace (ord 127)
                if (
                    len(new_char) == 1
                    and ord(new_char) == 127
                    and len(string_input) > 0
                ):
                    string_input = string_input[:-1]
                else:
                    string_input = string_input + new_char

                # Replace weird characters
                string_input = re.sub(
                    r"[^a-zA-Z0-9%s\n\r\w ]" % string.punctuation, "", string_input
                )

                # If we don't have a newline, continue adding on to new input
                if "\n" not in string_input and "\r" not in string_input:
                    os.write(openpty, terminal_input)
                    continue

                # If we are looking for history with up [A or down [B arrows
                # Note there is a preceding escape we are ignoring (ord 27)
                if "[A" in string_input or "[B" in string_input:
                    string_input = self.get_history(string_input.strip())

                # Universal exit command
                if "exit" in string_input:
                    print("\n\rContainer exited.\n\r")
                    return self.uri.extended_name

                # If no change, do not continue
                if not string_input:
                    continue

                # Add derived line to the history
                self.history.append(string_input)

                # Parse the command and determine if it's a match!
                executor = self.commands.get_executor(string_input)
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

                os.write(openpty, terminal_input)
                string_input = ""

            elif openpty in r:
                o = os.read(openpty, 10240)
                if o:
                    os.write(sys.stdout.fileno(), o)

    def __str__(self):
        return str(self.__class__.__name__)

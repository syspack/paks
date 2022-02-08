__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.utils.names import namer
from paks.logger import logger
import paks.utils
import paks.templates
import paks.signal

import subprocess
import select
import pty
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

        # If we weren't created with settings, add empty
        if not hasattr(self, "settings"):
            from paks.settings import EmptySettings

            self.settings = EmptySettings()

    def run_pty_command(self, cmd, ignore_control_c=True):
        """
        Run a command, return the pty, tty and subprocess p.
        """
        openpty, tty = pty.openpty()

        # Should we ignore control c?
        preexec_fn = None
        if ignore_control_c:
            preexec_fn = paks.signal.ignore_control_c
        p = subprocess.Popen(
            cmd, stdin=tty, stdout=tty, stderr=tty, preexec_fn=preexec_fn
        )
        return openpty, tty, p

    def encode(self, msg):
        return bytes((msg).encode("utf-8"))

    def command_listen(self, p, pty):
        """
        A wrapper to listen to and respond to terminal commands.
        """
        while p.poll() is None:
            try:
                r, _, _ = select.select([sys.stdin, pty], [], [])
            except KeyboardInterrupt:
                continue

            if sys.stdin in r:
                input_from_terminal = os.read(sys.stdin.fileno(), 10240)
                string_input = input_from_terminal.decode("utf-8")

                # University exit command
                if "exit" in string_input:
                    os.write(sys.stdout.fileno(), self.encode("Container exited. "))
                    return self.uri.extended_name

                # Check if this is a command to respond to
                # All commands require the container image and name (others are provided command line)
                executor = self.commands.get_executor(string_input)
                if executor:

                    # Provide pre-command message to the terminal
                    if executor.pre_message:
                        os.write(
                            sys.stdout.fileno(),
                            self.encode(executor.pre_message + "\n"),
                        )

                    # If we have an executor for the command, run it!
                    result = executor.run(
                        name=self.image,
                        container_name=self.uri.extended_name,
                        original=string_input,
                    )
                    if result.returncode != 0 and result.message:
                        logger.error(result.message)
                    elif result.message:
                        os.write(
                            sys.stdout.fileno(), self.encode(result.message + "\n")
                        )

                os.write(pty, input_from_terminal)

            elif pty in r:
                output_from_docker = os.read(pty, 10240)
                os.write(sys.stdout.fileno(), output_from_docker)

        listener.stop()

    def __str__(self):
        return str(self.__class__.__name__)

__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
import paks.commands
from .base import ContainerTechnology, ContainerName
import paks.utils

import subprocess


class DockerContainer(ContainerTechnology):
    """
    A Docker container controller.
    """

    command = "docker"

    def __init__(self, image, settings=None):
        if not paks.utils.which(self.command):
            logger.exit(
                "%s is required to use the '%s' base."
                % (self.command.capitalize(), self.command)
            )
        super(DockerContainer, self).__init__(settings)
        self.image = image
        self.uri = ContainerName(self.add_registry(image))
        self.commands = paks.commands.DockerCommands("docker")

    def run(self, shell):
        """
        Interactive shell into a container image.
        """
        cmd = [
            self.command,
            "run",
            "-it",
            "--rm",
            "--name",
            self.uri.extended_name,
            self.image,
            shell,
        ]
        name = self.interactive_command(cmd)

        # Remove the temporary container.
        if name:
            p = subprocess.Popen([self.command, "stop", name])
            p.wait()

    def add_registry(self, uri):
        """
        Given a "naked" name, add the registry if it's Docker Hub
        """
        # Is this a core library container, or Docker Hub without prefix?
        if uri.count("/") == 0:
            uri = "docker.io/library/%s" % uri
        elif uri.count("/") == 1:
            uri = "docker.io/%s" % uri
        return uri

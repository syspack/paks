__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
from .base import ContainerTechnology
import paks.utils

from datetime import datetime
import json
import os
import sys


class DockerContainer(ContainerTechnology):
    """
    A Docker container controller.
    """
    command = "docker"

    def __init__(self):
        if paks.utils.which(self.command)["return_code"] != 0:
            logger.exit(
                "%s is required to use the '%s' base."
                % (self.command.capitalize(), self.command)
            )
        super(DockerContainer, self).__init__()

    def shell(self, image):
        """
        Interactive shell into a container image.
        """
        os.system(
            "docker run -it --rm --entrypoint %s %s"
            % (self.settings.docker_shell, image)
        )

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

    def registry_pull(self, module_dir, container_dir, config, tag):
        """
        Pull a container to the library.
        """
        pull_type = config.get_pull_type()
        if pull_type != "docker":
            logger.exit("%s only supports Docker (oci registry) pulls." % self.command)

        tag_uri = "%s:%s" % (self.add_registry(config.docker), tag.name)
        tag_digest = "%s@%s" % (self.add_registry(config.docker), tag.digest)
        self.pull(tag_digest)
        # Podman doesn't keep a record of digest->tag, so we tag after
        return self.tag(tag_digest, tag_uri)

    def pull(self, uri):
        """
        Pull a unique resource identifier.
        """
        res = paks.utils.run_command([self.command, "pull", uri], stream=True)
        if res["return_code"] != 0:
            logger.exit("There was an issue pulling %s" % uri)
        return uri

    def tag(self, image, tag_as):
        """
        Given a container URI, tag as something else.
        """
        res = paks.utils.run_command([self.command, "tag", image, tag_as])
        if res["return_code"] != 0:
            logger.exit("There was an issue tagging %s as %s" % (image, tag_as))
        return tag_as

    def inspect(self, image):
        """
        Inspect an image
        """
        res = paks.utils.run_command([self.command, "inspect", image])
        if res["return_code"] != 0:
            logger.exit("There was an issue getting the manifest for %s" % image)
        raw = res["message"]
        return json.loads(raw)

    def exists(self, image):
        """
        Exists is a derivative of inspect that just determines existence.
        """
        if not image:
            return False
        res = paks.utils.run_command([self.command, "inspect", image])
        if res["return_code"] != 0:
            return False
        return True

    def get(self, module_name):
        """
        Determine if a container uri exists.
        """
        # If no module tag provided, try to deduce from install tree
        full_name = self.guess_tag(module_name, allow_fail=True)

        # The user already provided a tag
        if not full_name:
            full_name = module_name

        uri = self.add_registry(full_name)
        # If there isn't a tag in the name, add it back
        if ":" not in uri:
            uri = ":".join(uri.rsplit("/", 1))
        if uri and self.exists(uri):
            return uri

    def delete(self, image):
        """
        Delete a container when a module is deleted.
        """
        container = self.get(image)

        # If we can't get a specific image, the user wants to delete all tags
        # and we have more than one tag!
        if not container:
            tags = self.installed_tags(image)
            containers = ["%s:%s" % (image, tag) for tag in tags]
        else:
            containers = [container]

        for container in containers:
            if self.exists(container):
                paks.utils.run_command([self.command, "rmi", "--force", container])

    def test_script(self, image, test_script):
        """
        Given a test file, run it and respond accordingly.
        """
        command = [
            "docker",
            "run",
            "-i",
            "--entrypoint",
            "/bin/bash",
            "-t",
            image,
            test_script,
        ]
        result = paks.utils.run_command(command)

        # Return code
        return result["return_code"]

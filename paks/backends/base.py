__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
import paks.utils
import paks.templates

import os
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

    # TODO add custom functions here
    def __str__(self):
        return str(self.__class__.__name__)

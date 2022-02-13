__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.backends import get_container_backend
from .settings import Settings
from .env import Environment


class PakClient:
    """
    Paks has a main controller for interacting with paks.
    """

    def __init__(self, *args, **kwargs):
        settings_file = kwargs.get("settings_file")
        validate = kwargs.get("validate", True)
        if not hasattr(self, "settings"):
            self.settings = Settings(settings_file, validate=validate)
        self.env = Environment(self.settings.config_editor)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[paks-client]"

    def run(self, image, registry=None, shell=None, container_tech=None):
        """
        Run a paks image
        """
        shell = shell or self.settings.container_shell
        backend = get_container_backend(container_tech or self.settings.container_tech)

        # Pass settings to the backend!
        backend(image, self.settings).run(shell)

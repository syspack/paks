from .inspect import InspectContainer, Size
from .state import SaveContainer
from .env import EnvLoad, EnvHost, EnvSave
from .history import History
from .cp import Copy

# Based functions provided by paks
# These are currently all for docker and podman

# lookup of named commands and settings
docker_commands = {
    "#save": SaveContainer,
    "#inspect": InspectContainer,
    "#envload": EnvLoad,
    "#envhost": EnvHost,
    "#envsave": EnvSave,
    "#cp": Copy,
    "#size": Size,
}


class DockerCommands:

    # Required kwargs for any docker/podman command to run
    required = ["container_name", "name"]

    def __init__(self, container_tech):
        self.command = container_tech
        self.lookup = docker_commands

    def parse_name(self, cmd):
        parts = cmd.split(" ")
        return parts.pop(0).replace("\n", "").replace("\r", "").strip()

    def has_command(self, name):
        name, _ = self.parse_name(name)
        return name in self.lookup

    @property
    def history(self):
        return History(self.command)

    def get_executor(self, name, out=None):
        """
        Backend is required to update history
        """
        name = self.parse_name(name)
        if name in self.lookup:
            return self.lookup[name](self.command, required=self.required, out=out)

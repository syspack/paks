from .state import SaveContainer

# Based functions provided by paks
# These are currently all for docker and podman

# lookup of named commands and settings
docker_commands = {"#save": SaveContainer}


class Command:
    def __init__(self, name, cls, args):
        self.cls = cls
        self.name = name
        self.args = args


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

    def get_executor(self, name):
        name = self.parse_name(name)
        if name in self.lookup:
            return self.lookup[name](self.command, required=self.required)

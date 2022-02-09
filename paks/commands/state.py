__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.utils.names import namer
from .command import Command
import shutil
import tempfile
import os

# Every command must:
# 1. subclass Command
# 2. defined what container techs supported for (class attribute) defaults to all
# 3. define run function with kwargs


class SaveContainer(Command):

    supported_for = ["docker", "podman"]
    pre_message = "Saving container..."

    def run(self, **kwargs):
        """
        Save a temporary container name back to the main container name
        Available after check - validated self.kwargs
        """
        # Always run this first to make sure container tech is valid
        self.check(**kwargs)

        # These are both required for docker/podman
        container_name = self.kwargs["container_name"]
        name = self.kwargs["name"]
        tmp_name = container_name + "-" + namer.generate()

        # Not required, so we have a default
        suffix = self.kwargs.get("suffix", "-saved")

        # Run the command (show in real time)
        result = self.run_command([self.tech, "commit", container_name, tmp_name])
        if result:
            return result

        # Keep track of where we are to change back to
        here = os.getcwd()

        # Create a temporary context
        tempdir = tempfile.mkdtemp()
        dockerfile = os.path.join(tempdir, "Dockerfile")
        with open(dockerfile, "w") as fd:
            fd.write("FROM %s\n" % tmp_name)
        os.chdir(tempdir)

        result = self.run_command(
            [self.tech, "build", "--squash", "-t", name + suffix, "."], "error"
        )
        if result:
            return result

        result = self.run_command([self.tech, "rmi", tmp_name])
        if result:
            return result

        # Remove dangling None images (not recommended lol)
        os.system(
            '%s rmi --force $(%s images --filter "dangling=true" -q --no-trunc) >/dev/null 2>&1'
            % (self.tech, self.tech)
        )
        os.chdir(here)
        shutil.rmtree(tempdir)
        return self.return_success("Successfully saved container! ⭐️")

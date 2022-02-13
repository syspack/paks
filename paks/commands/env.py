__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from .command import Command
import os

# Every command must:
# 1. subclass Command
# 2. defined what container techs supported for (class attribute) defaults to all
# 3. define run function with kwargs


class EnvRemove(Command):

    supported_for = ["docker", "podman"]
    pre_message = "Saving environment variable..."
    parse_kwargs = False

    def run(self, **kwargs):
        """
        Save an environment variable to the host
        """
        self.check(**kwargs)

        if not self.args or len(self.args) < 2:
            return self.return_failure(
                "You must provide the environment name and at least one export."
            )
        envname = self.args.pop(0)
        self.env.load(envname)
        for envar in self.args:
            if not self.env.add(envname, envar, force=True):
                return self.return_failure(
                    "Could not add %s, did you include an =?" % envar
                )
            self.execute("export %s" % envar)
        return self.return_success(
            "Successfully added and exported environment variables."
        )


class EnvSave(Command):

    supported_for = ["docker", "podman"]
    pre_message = "Saving environment variable..."
    parse_kwargs = False

    def run(self, **kwargs):
        """
        Save an environment variable to the host
        """
        self.check(**kwargs)
        if not self.args or len(self.args) < 2:
            return self.return_failure(
                "You must provide the environment name and at least one export."
            )
        envname = self.args.pop(0)
        self.env.load(envname)
        for envar in self.args:
            if not self.env.add(envname, envar, force=True):
                return self.return_failure(
                    "Could not add %s, did you include an =?" % envar
                )
            self.execute("export %s" % envar)
        return self.return_success(
            "Successfully added and exported environment variables."
        )


class EnvHost(Command):

    supported_for = ["docker", "podman"]
    pre_message = "Getting host environment variable..."

    def run(self, **kwargs):
        """
        Retrieve an environment from the host.
        """
        # Always run this first to make sure container tech is valid
        self.check(**kwargs)

        # inspect defaults to labels and environment
        if not self.args:
            return self.return_failure(
                "You must provide the name of one or more environment variables."
            )

        # Load the environment variables
        found = False
        for name in self.args:
            value = os.environ.get(name)
            if not value:
                continue
            found = True
            self.execute("export %s=%s" % (name, value))

        if not found:
            return self.return_failure("No matching environment variables were found.")
        return self.return_success("Successfully loaded environment variables.")


class EnvLoad(Command):

    supported_for = ["docker", "podman"]
    pre_message = "Loading environment..."

    def run(self, **kwargs):
        """
        Load a named environment.
        """
        # Always run this first to make sure container tech is valid
        self.check(**kwargs)

        # inspect defaults to labels and environment
        if not self.args:
            return self.return_failure("You must provide the name of an environment.")

        # Load the environment!
        envname = self.args[0]
        self.env.load(envname)
        if not self.env.envars:
            return self.return_failure(
                "Environment %s does not have any variables." % envname
            )

        for key, value in self.env.envars.items():
            self.execute("export %s=%s" % (key, value))
        return self.return_success("Successfully loaded environment %s" % envname)

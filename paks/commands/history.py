__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from .command import Command

# Every command must:
# 1. subclass Command
# 2. defined what container techs supported for (class attribute) defaults to all
# 3. define run function with kwargs


class History(Command):

    supported_for = ["docker", "podman"]
    required = ["container_name"]

    def run(self, **kwargs):

        # Always run this first to make sure container tech is valid
        self.check(**kwargs)
        history_file = kwargs.get("history_file", "/root/.bash_history")
        self.out = self.kwargs.get("out", self.out)

        # These are both required for docker/podman
        container_name = self.kwargs["container_name"]
        out, err = self.execute_host(
            [
                self.tech,
                "exec",
                "-it",
                container_name,
                "/usr/bin/cat",
                history_file,
            ]
        )
        return out

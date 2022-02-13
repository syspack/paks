__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from .command import Command

# Every command must:
# 1. subclass Command
# 2. defined what container techs supported for (class attribute) defaults to all
# 3. define run function with kwargs


class InspectContainer(Command):

    supported_for = ["docker", "podman"]
    pre_message = "Inspecting Container..."

    def run(self, **kwargs):
        """
        Inspect a container fully, or specific sections
        """
        # Always run this first to make sure container tech is valid
        self.check(**kwargs)

        # These are both required for docker/podman
        container_name = self.kwargs["container_name"]

        # inspect defaults to labels and environment
        if self.args:
            for section in self.args:
                result = self.run_command(
                    [
                        self.tech,
                        "inspect",
                        "--format",
                        "{{json .%s }}" % section.capitalize(),
                        container_name,
                    ]
                )

        else:
            result = self.run_command([self.tech, "inspect", container_name])
            if result:
                return result
        return self.return_success()

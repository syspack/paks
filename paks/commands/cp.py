__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from .command import Command

# Every command must:
# 1. subclass Command
# 2. defined what container techs supported for (class attribute) defaults to all
# 3. define run function with kwargs


class Copy(Command):

    supported_for = ["docker", "podman"]
    pre_message = "Performing Copy..."

    def run(self, **kwargs):
        """
        Copy from host to container or vice versa
        """
        # Always run this first to make sure container tech is valid
        self.check(**kwargs)

        # These are both required for docker/podman
        container_name = self.kwargs["container_name"]

        # Args must have src and dst
        if len(self.args) != 2:
            return self.return_failure("You must provide a src and dest for copy.")

        src = self.args.pop(0)
        dest = self.args.pop(0)

        # src or dst must have host
        if "host:" not in src and "host:" not in dest:
            return self.return_failure(
                "One of copy arguments must be to the host:/path/to/file.txt"
            )

        args = {"src": src, "dest": dest}
        for argtype, path in args.items():
            if "host:" in path:
                path = path.replace("host:", "")
            else:
                path = "%s:%s" % (container_name, path)
            args[argtype] = path

        # docker cp!
        self.run_command([self.tech, "cp", args["src"], args["dest"]])
        return self.return_success()

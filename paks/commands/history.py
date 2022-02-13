__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from .command import Command
import readline
import shutil
import os
import sys

import subprocess
import tempfile

# Every command must:
# 1. subclass Command
# 2. defined what container techs supported for (class attribute) defaults to all
# 3. define run function with kwargs

class History(Command):

    supported_for = ["docker", "podman"]    
    required = ["container_name"]

    def run(self, **kwargs):

        # TODO require out passed in kwargs
        
        # Always run this first to make sure container tech is valid
        self.check(**kwargs)
        history_file = kwargs.get('history_file', "/tmp/history")
        self.out = self.kwargs.get("out", self.out)

        # Set the history to write to file
        self.run_hidden("history -a")

        # These are both required for docker/podman
        container_name = self.kwargs["container_name"]
        runcmd = ' cat $HISTFILE > %s' % history_file
        return self.execute_get(runcmd=runcmd, getcmd=[
                        self.tech,
                        "exec",
                        "-it",
                        container_name,
                       "/usr/bin/cat", history_file
                    ])

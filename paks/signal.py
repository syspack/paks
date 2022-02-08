__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import subprocess
import signal


def ignore_control_c():
    """
    We don't want subprocess to respond to control+C, so this will ignore it.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)

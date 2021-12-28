__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"


from paks.logger import logger
from subprocess import Popen, PIPE, STDOUT
import os


def which(software, strip_newline=True):
    """
    get_install gets path to installed software.
    """
    cmd = ["which", software]
    try:
        result = run_command(cmd)
        if strip_newline is True:
            result["message"] = result["message"].strip("\n")
        return result

    except:  # FileNotFoundError
        return None


def get_installdir():
    """get_installdir returns the installation directory of the application"""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def run_command(cmd, sudo=False, stream=False):
    """
    run_command uses subprocess to send a command to the terminal.

    Parameters
    ==========
    cmd: the command to send, should be a list for subprocess
    error_message: the error message to give to user if fails,
    if none specified, will alert that command failed.

    """
    stdout = PIPE if not stream else None
    if sudo is True:
        cmd = ["sudo"] + cmd

    try:
        output = Popen(cmd, stderr=STDOUT, stdout=stdout)

    except FileNotFoundError:
        cmd.pop(0)
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    t = output.communicate()[0], output.returncode
    output = {"message": t[0], "return_code": t[1]}

    if isinstance(output["message"], bytes):
        output["message"] = output["message"].decode("utf-8")

    return output

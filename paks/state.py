__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import threading
import subprocess
import signal
import random
import string
import select
import sys
import os


def run_container(name="ubuntu", entrypoint="bash"):
    """This function starts an interactive session with a container of interest.
    Run with threading, we can know when the container is exited for a final save.
    """
    import pty

    # This is ensuring every based image has just one saved name. This could
    # be managed more elegantly.
    random_name = name + "-" + generate_name()
    pty, tty = pty.openpty()
    p = subprocess.Popen(
        ["docker", "run", "-it", "--rm", "--name", random_name, name, entrypoint],
        stdin=tty,
        stdout=tty,
        stderr=tty,
    )

    # Keep updating the terminal until the user is done!
    # This is where we can read in commands and respond to user requests
    while True:
        try:
            return command_listen(p, pty, name, random_name)
        except KeyboardInterrupt:
            print("\nOops, we don't support Control+C yet!")

    # An non-intentional exit?
    return random_name


def command_listen(p, pty, name, random_name):
    """
    A wrapper to listen to and respond to terminal commands.
    """
    while p.poll() is None:
        r, _, _ = select.select([sys.stdin, pty], [], [])
        if sys.stdin in r:
            input_from_terminal = os.read(sys.stdin.fileno(), 10240)

            # Saving the state!
            if "#save" in input_from_terminal.decode("utf-8"):
                save_container(name, random_name)
                os.write(sys.stdout.fileno(), b"Saving container...\n")
            elif "exit" in input_from_terminal.decode("utf-8"):
                print("Container exited.")
                return random_name
            os.write(pty, input_from_terminal)
        elif pty in r:
            output_from_docker = os.read(pty, 10240)
            os.write(sys.stdout.fileno(), output_from_docker)


def save_container(name, container_name, suffix="-saved"):
    """
    Save a temporary container name back to the main container name
    """
    import subprocess
    import shutil
    import tempfile
    import os

    # A temporary name (probably this should be random!)
    tmp_name = container_name + "-tmp"

    # Probably this should be random!
    p = subprocess.Popen(["docker", "commit", container_name, tmp_name])
    p.wait()

    # Keep track of where we are to change back to
    here = os.getcwd()

    # Create a temporary context
    tempdir = tempfile.mkdtemp()
    dockerfile = os.path.join(tempdir, "Dockerfile")
    with open(dockerfile, "w") as fd:
        fd.write("FROM %s\n" % tmp_name)
    os.chdir(tempdir)
    p = subprocess.Popen(["docker", "build", "--squash", "-t", name + suffix, "."])
    p.wait()
    p = subprocess.Popen(["docker", "rmi", tmp_name])
    p.wait()

    # Remove dangling None images (not recommended lol)
    os.system('docker rmi $(docker images --filter "dangling=true" -q --no-trunc)')
    os.chdir(here)
    shutil.rmtree(tempdir)


def main():
    """Start a thread to run the container, and we can run other tasks too."""
    # threading.Thread(target=run_container, name='run-container').start()
    # Perform other tasks while the thread is running.
    name = run_container()

    # Remove the temporary container.
    if name:
        p = subprocess.Popen(["docker", "stop", name])
        p.wait()


if __name__ == "__main__":
    main()

from paks.logger import logger
from .podman import PodmanContainer
from .docker import DockerContainer


def get_container_backend(name, settings=None):
    techs = {
        "docker": DockerContainer,
        "podman": PodmanContainer,
    }
    if name.lower() not in techs:
        logger.exit("%s is not a known container backend." % name.lower())

    return techs[name.lower()]

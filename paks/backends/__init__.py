from paks.logger import logger
from .singularity import SingularityContainer
from .podman import PodmanContainer
from .docker import DockerContainer


def get_container_backend(name):
    techs = {
        "docker": DockerContainer,
        "podman": PodmanContainer,
        "singularity": SingularityContainer,
    }
    if name.lower() not in techs:
        logger.exit("%s is not a known container backend." % name.lower())
    return techs[name.lower()]

from enum import StrEnum

from client import ScalrClient
from port_ocean.context.ocean import ocean


class ObjectKind(StrEnum):
    ENVIRONMENT = "environment"
    WORKSPACE = "workspace"
    RUN = "run"
    MODULE = "module"


def init_scalr_client() -> ScalrClient:
    config = ocean.integration_config
    return ScalrClient(
        config["scalr_base_url"],
        config["scalr_token"],
    )

from loguru import logger

from port_ocean.context.ocean import ocean
from port_ocean.core.ocean_types import ASYNC_GENERATOR_RESYNC_TYPE
from utils import ObjectKind, init_scalr_client


@ocean.on_resync(ObjectKind.ENVIRONMENT)
async def resync_environments(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    scalr_client = init_scalr_client()
    async for environments in scalr_client.get_environments():
        logger.info(f"Received {len(environments)} batch {kind}s")
        yield environments


@ocean.on_resync(ObjectKind.WORKSPACE)
async def resync_workspaces(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    scalr_client = init_scalr_client()
    async for workspaces in scalr_client.get_workspaces():
        logger.info(f"Received {len(workspaces)} batch {kind}s")
        yield workspaces


@ocean.on_resync(ObjectKind.RUN)
async def resync_runs(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    scalr_client = init_scalr_client()
    async for workspaces in scalr_client.get_workspaces():
        for workspace in workspaces:
            async for runs in scalr_client.get_runs_for_workspace(workspace["id"]):
                logger.info(f"Received {len(runs)} {kind}s for workspace {workspace['id']}")
                yield runs


@ocean.on_resync(ObjectKind.MODULE)
async def resync_modules(kind: str) -> ASYNC_GENERATOR_RESYNC_TYPE:
    scalr_client = init_scalr_client()
    async for modules in scalr_client.get_modules():
        logger.info(f"Received {len(modules)} batch {kind}s")
        yield modules


@ocean.on_start()
async def on_start() -> None:
    logger.info("Starting Port Ocean Scalr integration")

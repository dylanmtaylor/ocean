from typing import Any, AsyncGenerator, Optional
from aiolimiter import AsyncLimiter
from loguru import logger

from port_ocean.utils import http_async_client

PAGE_SIZE = 20
NUMBER_OF_REQUESTS = 25
NUMBER_OF_SECONDS = 1


class ScalrClient:
    def __init__(self, scalr_base_url: str, auth_token: str) -> None:
        self.api_url = f"https://{scalr_base_url}/api/iacp/v3"
        self.base_headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }
        self.client = http_async_client
        self.client.headers.update(self.base_headers)
        self.rate_limiter = AsyncLimiter(NUMBER_OF_REQUESTS, NUMBER_OF_SECONDS)

    async def _send_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        async with self.rate_limiter:
            response = await self.client.request(
                method=method, url=url, params=params
            )
            response.raise_for_status()
            return response.json()

    async def _get_paginated(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        params = params or {}
        params["page[size]"] = PAGE_SIZE
        page_number = 1

        while True:
            params["page[number]"] = page_number
            response = await self._send_request(endpoint, params=params)
            data = response.get("data", [])
            if not data:
                break
            logger.info(f"Fetched {len(data)} items from {endpoint} page {page_number}")
            yield data

            pagination = response.get("meta", {}).get("pagination", {})
            total_pages = pagination.get("total-pages", page_number)
            if page_number >= total_pages:
                break
            page_number += 1

    async def get_environments(
        self,
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        async for batch in self._get_paginated("environments"):
            yield batch

    async def get_workspaces(
        self,
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        async for batch in self._get_paginated("workspaces"):
            yield batch

    async def get_runs_for_workspace(
        self, workspace_id: str
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        async for batch in self._get_paginated(
            "runs", params={"filter[workspace]": workspace_id}
        ):
            yield batch

    async def get_modules(
        self,
    ) -> AsyncGenerator[list[dict[str, Any]], None]:
        async for batch in self._get_paginated(
            "modules", params={"include": "module-versions"}
        ):
            yield batch

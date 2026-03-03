"""Core async HTTP client with connection pooling and retry logic"""

import asyncio
from typing import Any

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from bdfinance import constants
from bdfinance.config import ClientConfig

logger = structlog.get_logger()


class AsyncHTTPClient:
    """Async HTTP client with connection pooling, retries, and rate limiting"""

    def __init__(self, config: ClientConfig | None = None) -> None:
        self.config = config or ClientConfig()
        self._client: httpx.AsyncClient | None = None
        self._semaphore = asyncio.Semaphore(self.config.rate_limit)
        self._base_headers = {
            "User-Agent": constants.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.close()

    async def start(self) -> None:
        """Initialize the HTTP client"""
        if self._client is None:
            limits = httpx.Limits(
                max_connections=self.config.max_connections,
                max_keepalive_connections=self.config.max_keepalive_connections,
            )
            timeout = httpx.Timeout(self.config.timeout)

            self._client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                headers=self._base_headers,
                follow_redirects=True,
                http2=True,
            )
            logger.info("HTTP client initialized", limits=limits)

    async def close(self) -> None:
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("HTTP client closed")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        use_alt_url: bool = False,
    ) -> httpx.Response:
        """Make a GET request with retries and rate limiting"""
        if self._client is None:
            raise RuntimeError("HTTP client not initialized. Call start() first.")

        async with self._semaphore:
            base_url = self.config.dse_alt_url if use_alt_url else self.config.dse_url
            # full_url = f"{base_url}{url}"
            full_url = url if url.startswith("http") else f"{base_url}{url}"

            logger.debug(
                "Making GET request",
                url=full_url,
                params=params,
                use_alt_url=use_alt_url,
            )

            try:
                response = await self._client.get(
                    full_url,
                    params=params,
                    headers=headers or {},
                )
                response.raise_for_status()
                logger.debug("GET request successful", status=response.status_code)
                return response

            except httpx.HTTPStatusError as e:
                logger.warning(
                    "HTTP status error",
                    status=e.response.status_code,
                    url=full_url,
                )
                # Try alternate URL if primary fails
                if not use_alt_url and e.response.status_code >= 500:
                    logger.info("Retrying with alternate URL")
                    return await self.get(url, params, headers, use_alt_url=True)
                raise

            except httpx.RequestError as e:
                logger.error("Request error", error=str(e), url=full_url)
                raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        use_alt_url: bool = False,
    ) -> httpx.Response:
        """Make a POST request with retries and rate limiting"""
        if self._client is None:
            raise RuntimeError("HTTP client not initialized. Call start() first.")

        async with self._semaphore:
            base_url = self.config.dse_alt_url if use_alt_url else self.config.dse_url
            full_url = f"{base_url}{url}"

            logger.debug(
                "Making POST request",
                url=full_url,
                data=data,
                params=params,
                use_alt_url=use_alt_url,
            )

            try:
                response = await self._client.post(
                    full_url,
                    data=data,
                    params=params,
                    headers=headers or {},
                )
                response.raise_for_status()
                logger.debug("POST request successful", status=response.status_code)
                return response

            except httpx.HTTPStatusError as e:
                logger.warning(
                    "HTTP status error",
                    status=e.response.status_code,
                    url=full_url,
                )
                # Try alternate URL if primary fails
                if not use_alt_url and e.response.status_code >= 500:
                    logger.info("Retrying with alternate URL")
                    return await self.post(url, data, params, headers, use_alt_url=True)
                raise

            except httpx.RequestError as e:
                logger.error("Request error", error=str(e), url=full_url)
                raise

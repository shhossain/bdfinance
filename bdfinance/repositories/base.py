from collections.abc import Callable
from typing import Any, TypedDict

import pandas as pd
from bdfinance.cache import CacheManager
from bdfinance.http_client import AsyncHTTPClient
from bdfinance.parsers import HTMLParser
from structlog import get_logger

logger = get_logger()


class RequestPayload(TypedDict, total=False):
    url: str
    key: str
    parser: str | Callable | None
    ttl: int | None
    data: dict | None
    method: str | None


class BaseRepository:
    def __init__(
        self,
        http_client: AsyncHTTPClient,
        cache_manager: CacheManager | None = None,
    ) -> None:
        self.http = http_client
        self.cache = cache_manager
        self.parser = HTMLParser()

    async def get_data(self, payload: RequestPayload) -> Any | None:
        if (
            not payload.get("url")
            or not payload.get("key")
            or not payload.get("parser")
        ):
            raise ValueError("Payload must contain 'url', 'key', and 'parser' fields.")

        key = payload.get("key", "")
        url = payload.get("url", "")
        parser = payload.get("parser", None)

        if self.cache:
            cached_data = await self.cache.get(key)
            if cached_data is not None:
                return cached_data

        if payload.get("method", "GET") == "GET":
            response = await self.http.get(url, params=payload.get("data"))
        else:
            response = await self.http.post(url, data=payload.get("data"))

        html_content = response.text
        if isinstance(parser, str):
            if not hasattr(self.parser, parser):
                raise ValueError(f"Parser method '{parser}' not found in HTMLParser.")
            parse_method = getattr(self.parser, parser)
            data = parse_method(html_content)
        elif callable(parser):
            data = parser(html_content)
        else:
            raise ValueError("Invalid parser provided in payload.")

        if data is None:
            logger.warning(f"No data parsed from {url}")
            return None

        if self.cache:
            await self.cache.set(key, data, ttl=payload.get("ttl") or 3600)

        return data

    async def get_dataframe(self, payload: RequestPayload):
        if not payload.get("url") or not payload.get("key"):
            raise ValueError("Payload must contain 'url' and 'key' fields.")

        key = payload.get("key", "")
        url = payload.get("url", "")
        parser = payload.get("parser", None)

        if self.cache:
            cached_data = await self.cache.get(key)
            if cached_data is not None:
                return cached_data
        if payload.get("method", "GET") == "GET":
            response = await self.http.get(url, params=payload.get("data"))
        else:
            response = await self.http.post(url, data=payload.get("data"))

        html_content = response.text
        # with open("debug.html", "w", encoding="utf-8") as f:
        #     f.write(html_content)

        if isinstance(parser, str):
            if not hasattr(self.parser, parser):
                raise ValueError(f"Parser method '{parser}' not found in HTMLParser.")

            parse_method = getattr(self.parser, parser)
            data = parse_method(html_content)
        elif callable(parser):
            data = parser(html_content)
        else:
            logger.error("No valid parser provided in payload.")
            data = self.parser.parse_price_table(html_content)

        if data is None:
            logger.warning(f"No data parsed from {url}")
            return pd.DataFrame()

        dataframe = pd.DataFrame(data)

        if self.cache:
            await self.cache.set(key, dataframe, ttl=payload.get("ttl") or 3600)

        return dataframe

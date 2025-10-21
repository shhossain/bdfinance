"""Market data repository with async methods"""

import asyncio
from datetime import datetime
from typing import Literal
import pandas as pd
import structlog

from bdfinance import constants
from bdfinance.models.market import MarketDepth
from bdfinance.repositories.base import BaseRepository, RequestPayload
from bdfinance.utils.date_helper import convert_to_start_end_date
from bdfinance.utils.parse_com_info import DSECompanyData

logger = structlog.get_logger()


class MarketRepository(BaseRepository):
    """Repository for market data operations"""

    async def get_company_summary(self, name: str) -> str | None:
        """Get company summary by name"""
        # Check cache
        if self.cache:
            cached = await self.cache.get("company_summary", name=name)
            if cached:
                return cached

        params = {
            "prop": "extracts|info",
            "inprop": "url",
            "explaintext": "",
            "exintro": "",
            "exsentences": "5",
            "format": "json",
            "action": "query",
            "formatversion": "2",
        }
        qparams = {
            "list": "search",
            "srsearch": name,
            "srlimit": 1,
            "srnamespace": 0,
            "srprop": "snippet|titlesnippet|size|wordcount|timestamp",
            "format": "json",
            "action": "query",
            "formatversion": "2",
        }

        res = await self.http.get(constants.WIKIPEDIA_API_URL, params=qparams)
        r = res.json()
        data = r.get("query", {}).get("search", [])
        title = data[0]["title"] if data else name

        params["titles"] = title
        res = await self.http.get(constants.WIKIPEDIA_API_URL, params=params)
        r = res.json()

        pages = r.get("query", {}).get("pages", [])
        page_data = pages[0] if pages else {}
        summary = page_data.get("extract", "")

        if not summary:
            logger.warning("No summary found", name=name, title=title)
            return None

        if self.cache and summary:
            await self.cache.set(
                "company_summary", summary, name=name, ttl=86400
            )  # 1 day

        return summary

    async def get_company_info(
        self,
        symbol: str,
        summary: bool | None = None,
    ) -> DSECompanyData | None:
        """
        Get company information (alias for get_company_inf)

        Args:
            symbol: Stock symbol
            summary: Whether to fetch company summary from Wikipedia

        Returns:
            Company information as Pydantic model
        """
        # Fetch data using get_data
        payload: RequestPayload = {
            "url": constants.DSE_COMPANY_INFO_URL,
            "key": f"company_info_{symbol}",
            "parser": "parse_company_info",
            "data": {"name": symbol},
            "method": "GET",
            "ttl": 3600,
        }
        data = await self.get_data(payload)

        if summary and data:
            # Get company summary from Wikipedia
            company_name = data.basic_information.company_name or symbol
            if company_name:
                try:
                    summary_text = await self.get_company_summary(company_name)
                    # Update basic_information with summary
                    data.basic_information.summary = summary_text
                except Exception as e:
                    logger.error(
                        "Failed to fetch company summary", symbol=symbol, error=str(e)
                    )

        return data

    async def get_latest_pe(self) -> pd.DataFrame:
        """Get latest P/E ratios"""
        payload = {
            "url": constants.DSE_LPE_URL,
            "key": "latest_pe",
            "parser": "parse_latest_pe",
            "ttl": 3600,
        }
        return await self.get_dataframe(RequestPayload(**payload))

    async def get_market_overview(
        self,
        start: str | datetime | None = None,
        end: str | datetime | None = None,
        period: str | None = None,
    ) -> pd.DataFrame:
        """Get extended market information"""
        start, end = convert_to_start_end_date(
            start=start,
            end=end,
            period=period,
            default_period="30d",
            format="%Y-%m-%d",
        )

        payload = {
            "url": constants.DSE_MARKET_INFO_MORE_URL,
            "key": f"market_inf_more_{start}_{end}",
            "parser": "parse_market_info",
            "data": {
                "startDate": start,
                "endDate": end,
                "searchRecentMarket": "Search Recent Market",
            },
            "ttl": 3600,
            "method": "POST",
        }
        return await self.get_dataframe(RequestPayload(**payload))

    async def get_market_depth(self, symbol: str) -> MarketDepth | None:
        """
        Get market depth for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Market depth data or None
        """
        # Fetch data using get_data
        payload: RequestPayload = {
            "url": constants.DSE_MARKET_DEPTH_URL,
            "key": f"market_depth_{symbol}",
            "parser": "parse_market_depth",
            "data": {"inst": symbol},
            "method": "POST",
            "ttl": 60,
        }

        depth_data = await self.get_data(payload)

        if not depth_data:
            return None

        # Parse with Pydantic
        depth_list = [MarketDepth(**data) for data in depth_data]

        return depth_list[0] if depth_list else None

    async def get_market_depth_batch(
        self, symbols: list[str]
    ) -> dict[str, list[MarketDepth]]:
        """Batch fetch market depth for multiple instruments"""
        logger.info("Batch fetching market depth", instrument_count=len(symbols))

        # Create tasks for parallel execution
        tasks = [self.get_market_depth(sym) for sym in symbols]

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dict
        result_dict = {}
        for inst, result in zip(symbols, results, strict=True):
            if isinstance(result, Exception):
                logger.error(
                    "Failed to fetch market depth", instrument=inst, error=str(result)
                )
                result_dict[inst] = []
            else:
                result_dict[inst] = result

        logger.info("Batch market depth fetch complete", instrument_count=len(symbols))
        return result_dict

    async def get_sector_listed(self) -> pd.DataFrame:
        """Get list of sectors"""
        payload = {
            "url": constants.DSE_SECTOR_LIST_URL,
            "key": "sector_list",
            "parser": "parse_sector_list",
            "ttl": 86400,
        }
        return await self.get_dataframe(RequestPayload(**payload))

    async def get_latest_share_price_by_sector(self, sector: str) -> pd.DataFrame:
        """Get latest share price by sector"""
        if isinstance(sector, str) and not sector.isdigit():
            sectors = await self.get_sector_listed()
            if sectors is None or "Code" not in sectors.columns:
                logger.error("Sector data not available")
                return pd.DataFrame()
            sector_row = sectors[sectors["Sector"].str.lower() == sector.lower()]
            if sector_row.empty:
                logger.error("Sector not found", sector=sector)
                return pd.DataFrame()
            sector_code = sector_row.iloc[0]["Code"]
            if sector_code is None:
                logger.error("Sector code not found in detail link", sector=sector)
                return pd.DataFrame()
            sector = str(sector_code)

        payload: RequestPayload = {
            "url": constants.DSE_LTP_URL,
            "key": f"latest_share_price_by_sector_{sector}",
            "parser": "parse_latest_share_price",
            "data": {"area": str(sector)},
            "method": "GET",
            "ttl": 3600,
        }

        df = await self.get_dataframe(payload)

        if df.empty:
            logger.warning("No latest share price data found for sector", sector=sector)

        return df

    async def get_top_stocks(self) -> pd.DataFrame:
        """Get top performing stocks"""
        payload = {
            "url": constants.DSE_TOP_STOCKS_URL,
            "key": "top_stocks",
            "parser": "parse_top_stocks",
            "ttl": 3600,
        }

        return await self.get_dataframe(RequestPayload(**payload))

    async def get_top_10(self, type: Literal["gainers", "losers"]) -> pd.DataFrame:
        """Get top 10 gainers"""
        payload = {
            "url": constants.DSE_TOP_10_GAINERS_URL
            if type == "gainers"
            else constants.DSE_TOP_10_LOSERS_URL,
            "key": f"top_10_{type}",
            "parser": "parse_top_10",
            "ttl": 3600,
        }
        return await self.get_dataframe(RequestPayload(**payload))

    async def get_top_10_losers(self) -> pd.DataFrame:
        """Get top 10 losers"""
        return await self.get_top_10(type="losers")

    async def get_top_10_gainers(self) -> pd.DataFrame:
        """Get top 10 gainers"""
        return await self.get_top_10(type="gainers")

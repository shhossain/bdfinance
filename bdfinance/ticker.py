"""Unified Ticker interface for DSE stocks - similar to yfinance

This module provides a simple, unified interface for accessing all data
related to a specific stock symbol.
"""

import asyncio
from datetime import datetime
from typing import Any
import pandas as pd
from bdfinance.cache import CacheManager
from bdfinance.http_client import AsyncHTTPClient
from bdfinance.models.market import MarketDepth
from bdfinance.models.news import AGMNews, News
from bdfinance.models.trading import CurrentTradeData
from bdfinance.repositories.market import MarketRepository
from bdfinance.repositories.news import NewsRepository
from bdfinance.repositories.trading import TradingRepository
from bdfinance.utils.data_cleaners import clean_symbol
from bdfinance.utils.date_helper import convert_to_start_end_date
from bdfinance.utils.parse_com_info import DSECompanyData


class Ticker:
    """
    Unified interface for accessing stock data from DSE

    Usage:
        async with BDStockClient() as client:
            ticker = client.ticker("ACI")

            # Get current quote
            quote = await ticker.quote()

            # Get historical data
            history = await ticker.history(start="2024-01-01", end="2024-12-31")

            # Get company info
            info = await ticker.info()

            # Get market depth
            depth = await ticker.depth()

            # Get news
            news_list = await ticker.news()
    """

    def __init__(
        self,
        symbol: str,
        http_client: AsyncHTTPClient,
        cache_manager: CacheManager | None = None,
    ):
        """
        Initialize ticker for a specific symbol

        Args:
            symbol: Stock symbol (e.g., "ACI", "BEXIMCO")
            http_client: Shared HTTP client instance
            cache_manager: Shared cache manager instance (optional)
        """
        self.symbol = clean_symbol(symbol)
        self._http_client = http_client
        self._cache_manager = cache_manager

        # Initialize repositories
        self._trading_repo = TradingRepository(http_client, cache_manager)
        self._market_repo = MarketRepository(http_client, cache_manager)
        self._news_repo = NewsRepository(http_client, cache_manager)

    async def quote(self) -> CurrentTradeData | None:
        """
        Get current trading data (quote) for this symbol

        Returns:
            Current trade data or None if not found
        """
        return await self._trading_repo.get_quote(symbol=self.symbol)

    async def history(
        self,
        start: str | datetime | None = None,
        end: str | datetime | None = None,
        period: str | None = None,
    ) -> pd.DataFrame:
        """
        Get historical trading data for this symbol

        Args:
            start: Start date (YYYY-MM-DD format or datetime)
            end: End date (YYYY-MM-DD format or datetime)

        Returns:
            Historical data as DataFrame or list
        """
        start_date, end_date = convert_to_start_end_date(
            start=start,
            end=end,
            period=period,
            default_period="30d",
            format="%Y-%m-%d",
        )

        all_data = await self._trading_repo.get_history(
            start=start_date,
            end=end_date,
            symbol=self.symbol,
        )
        return all_data

    async def info(self, summary: bool | None = None) -> DSECompanyData | None:
        """
        Get company information for this symbol

        Returns:
            Company information
        """
        return await self._market_repo.get_company_info(
            symbol=self.symbol, summary=summary
        )

    async def depth(self) -> MarketDepth | None:
        """
        Get market depth data for this symbol

        Returns:
            Market depth or None if not found
        """
        return await self._market_repo.get_market_depth(symbol=self.symbol)

    async def news(self) -> list[News]:
        """
        Get news related to this company

        Returns:
            List of news items
        """
        # Get news for this symbol
        return await self._news_repo.get_all_news(symbol=self.symbol)

    async def agm_news(self) -> list[AGMNews]:
        """
        Get AGM news for this company

        Returns:
            List of AGM news items
        """
        all_agm = await self._news_repo.get_agm_news()

        # Filter by company name (AGMNews uses company, not symbol)
        return [item for item in all_agm if self.symbol.upper() in item.company.upper()]

    async def fundamentals(self) -> dict[str, Any]:
        """
        Get fundamental data for this symbol

        Returns comprehensive fundamental data including:
        - Current quote
        - Company info
        - Latest PE data (if available)

        Returns:
            Dictionary with fundamental data
        """

        quote_task = self.quote()
        info_task = self.info()
        pe_task = self._market_repo.get_latest_pe()

        quote, info, pe_data = await asyncio.gather(
            quote_task,
            info_task,
            pe_task,
            return_exceptions=True,
        )

        # Find PE data for this symbol
        pe_info = None
        if isinstance(pe_data, pd.DataFrame):
            pe_row = pe_data[pe_data["Symbol"].str.upper() == self.symbol.upper()]
            if not pe_row.empty:
                pe_info = pe_row.iloc[0].to_dict()

        return {
            "symbol": self.symbol,
            "quote": quote,
            "company_info": info,
            "pe_data": pe_info,
        }

    def __repr__(self) -> str:
        return f"Ticker(symbol='{self.symbol}')"

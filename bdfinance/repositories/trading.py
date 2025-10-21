"""Trading data repository with async methods and batch processing"""

import asyncio
from datetime import datetime
from typing import overload

import pandas as pd
import structlog

from bdfinance import constants
from bdfinance.models.trading import (
    CurrentTradeData,
    TradingSymbol,
)
from bdfinance.repositories.base import BaseRepository, RequestPayload
from bdfinance.utils.common import convert_dict_keys_to_lower
from bdfinance.utils.date_helper import convert_to_start_end_date

logger = structlog.get_logger()


class TradingRepository(BaseRepository):
    """Repository for trading data operations"""

    @overload
    async def get_quote(
        self,
        symbol: str,
    ) -> CurrentTradeData | None: ...

    @overload
    async def get_quote(
        self,
        symbol: list[str],
    ) -> dict[str, CurrentTradeData | None]: ...

    @overload
    async def get_quote(
        self,
        symbol: None = None,
    ) -> list[CurrentTradeData]:
        """
        Get current quote for list of symbol(s) (alias for get_current_trade_data)

        Args:
            symbol: Stock symbol

        Returns:
            Dict of symbol to Current trade data or None
        """
        ...

    async def get_quote(
        self,
        symbol: str | list[str] | None = None,
    ) -> (
        list[CurrentTradeData]
        | CurrentTradeData
        | None
        | dict[str, CurrentTradeData | None]
    ):
        """
        Get current quote for a symbol(s) (alias for get_current_trade_data)

        Args:
            symbol: Stock symbol

        Returns:
            Current trade data or None
        """
        # Fetch data using get_data
        payload: RequestPayload = {
            "url": constants.DSE_LSP_URL,
            "key": "current_trade_data",
            "parser": "parse_current_trade_data",
            "method": "GET",
            "ttl": 3600,
        }
        quotes_data = await self.get_data(payload)

        if not quotes_data:
            if symbol is None:
                return []
            elif isinstance(symbol, str):
                return None
            else:
                return {sym: None for sym in symbol}

        # Parse with Pydantic
        quotes = [
            CurrentTradeData(**convert_dict_keys_to_lower(quote))
            for quote in quotes_data
        ]

        # Handle different input types
        if symbol is None:
            # Return all quotes
            return quotes
        elif isinstance(symbol, str):
            # Single symbol - check cache first
            if self.cache:
                cached = await self.cache.get("current_trade", symbol=symbol)
                if cached:
                    return cached

            # Filter by symbol
            filtered = [q for q in quotes if q.symbol == symbol.upper()]
            result = filtered[0] if filtered else None

            # Cache result
            if self.cache:
                await self.cache.set("current_trade", result, symbol=symbol)

            return result
        else:
            # List of symbols - check cache first
            if self.cache:
                cached_results = {}
                uncached_symbols = []
                for sym in symbol:
                    cached = await self.cache.get("current_trade", symbol=sym)
                    if cached:
                        cached_results[sym] = cached
                    else:
                        uncached_symbols.append(sym)

                if uncached_symbols:
                    # Create lookup dict for uncached symbols
                    data_map = {quote.symbol: quote for quote in quotes}
                    for sym in uncached_symbols:
                        result = data_map.get(sym.upper())
                        cached_results[sym] = result
                        # Cache individual result
                        await self.cache.set("current_trade", result, symbol=sym)

                return cached_results
            else:
                # No cache - create lookup dict
                data_map = {quote.symbol: quote for quote in quotes}
                return {sym.upper(): data_map.get(sym.upper()) for sym in symbol}

    async def get_dsex_quote(
        self,
        symbol: str | None = None,
    ) -> list[CurrentTradeData] | CurrentTradeData | None:
        """Get DSEX share price data"""
        payload: RequestPayload = {
            "url": constants.DSEX_INDEX_VALUE,
            "key": "dsex_data" + (f"_{symbol}" if symbol else "_all"),
            "parser": "parse_current_trade_data",
            "method": "GET",
            "ttl": 3600,
        }
        data = await self.get_data(payload)
        if data is None:
            return None
        quotes = [
            CurrentTradeData(**convert_dict_keys_to_lower(quote)) for quote in data
        ]
        if symbol:
            filtered = [q for q in quotes if q.symbol == symbol.upper()]
            result = filtered[0] if filtered else None
        else:
            result = quotes

        return result

    async def get_trading_symbols(self) -> list[TradingSymbol]:
        """Get all trading symbols"""
        # Fetch data using get_data
        payload: RequestPayload = {
            "url": constants.DSE_LSP_URL,
            "key": "trading_symbols",
            "parser": "parse_current_trade_data",
            "method": "GET",
            "ttl": 3600,
        }
        quotes_data = await self.get_data(payload)

        if not quotes_data:
            return []

        # Extract symbols
        codes = [TradingSymbol(symbol=quote["Symbol"]) for quote in quotes_data]

        return codes

    @overload
    async def get_history(
        self,
        start: str | datetime | None = None,
        end: str | datetime | None = None,
        period: str | None = None,
    ) -> pd.DataFrame: ...

    @overload
    async def get_history(
        self,
        start: str | datetime | None = None,
        end: str | datetime | None = None,
        period: str | None = None,
        symbol: str = ...,
    ) -> pd.DataFrame: ...

    @overload
    async def get_history(
        self,
        start: str | datetime | None = None,
        end: str | datetime | None = None,
        period: str | None = None,
        symbol: list[str] = ...,
    ) -> dict[str, pd.DataFrame]: ...

    async def get_history(
        self,
        start: str | datetime | None = None,
        end: str | datetime | None = None,
        period: str | None = None,
        symbol: str | list[str] = "All Instrument",
    ) -> pd.DataFrame | dict[str, pd.DataFrame]:
        """
        Get historical price data (alias for get_hist_data)

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            symbol: Stock symbol (default: all instruments)

        Returns:
            DataFrame with historical data
        """
        start, end = convert_to_start_end_date(
            start=start, end=end, period=period, format="%Y-%m-%d"
        )
        if isinstance(symbol, str):
            payload: RequestPayload = {
                "url": (
                    constants.DSE_MARKET_SUMMARY_URL
                    if symbol == "DSEX"
                    else constants.DSE_DEA_URL
                ),
                "key": f"hist_data_{symbol}_{start}_{end}",
                "data": {
                    "startDate": start,
                    "endDate": end,
                    **({} if symbol == "DSEX" else {"inst": symbol}),
                    "archive": "data",
                },
                "parser": (
                    "parse_index_data" if symbol == "DSEX" else "parse_historical_data"
                ),
                "method": "GET",
                "ttl": 3600,
            }
            df = await self.get_dataframe(payload)
            return df
        else:
            # List of symbols - batch processing
            logger.info(
                "Batch fetching historical data",
                symbol_count=len(symbol),
                start=start,
                end=end,
            )

            # Create tasks for parallel execution
            tasks = [self.get_history(start, end, symbol) for symbol in symbol]

            # Execute concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Build result dict
            result_dict = {}
            for sym, result in zip(symbol, results, strict=False):
                if isinstance(result, Exception):
                    logger.error(
                        "Failed to fetch historical data", symbol=sym, error=str(result)
                    )
                    result_dict[sym] = pd.DataFrame()
                else:
                    result_dict[sym] = result

            logger.info("Batch historical fetch complete", symbol_count=len(symbol))
            return result_dict

    async def get_basic_historical(
        self,
        start: str | datetime,
        end: str | datetime,
        code: str = "All Instrument",
        index: bool = False,
    ) -> pd.DataFrame:
        """Get basic historical data (OHLCV)"""
        # Check cache
        start, end = convert_to_start_end_date(start=start, end=end, format="%Y-%m-%d")

        payload: RequestPayload = {
            "url": constants.DSE_DEA_URL,
            "key": f"basic_hist_data_{start}_{end}_{code}",
            "parser": "parse_historical_data",
            "data": {
                "startDate": start,
                "endDate": end,
                "inst": code,
                "archive": "data",
            },
            "method": "GET",
            "ttl": 3600,
        }

        # Fetch data using get_data
        hist_data = await self.get_data(payload)

        # Convert to basic format
        if hist_data:
            basic_data = []
            for item in hist_data:
                try:
                    basic_data.append(
                        {
                            "date": item["date"],
                            "open": float(item["open"].replace(",", "")),
                            "high": float(item["high"].replace(",", "")),
                            "low": float(item["low"].replace(",", "")),
                            "close": float(item["close"].replace(",", "")),
                            "volume": int(item["volume"].replace(",", "")),
                        }
                    )
                except (KeyError, ValueError) as e:
                    logger.warning("Failed to parse data row", error=str(e))
                    continue

            df = pd.DataFrame(basic_data)
            if "date" in df.columns and index:
                df = df.set_index("date")
            df = df.sort_index(ascending=True) if index else df
        else:
            df = pd.DataFrame()
            logger.warning("No basic historical data found")

        return df

    async def get_close_price(
        self,
        start: str | datetime,
        end: str | datetime,
        symbol: str = "All Instrument",
    ) -> pd.DataFrame:
        """Get close price data"""
        # Check cache
        start, end = convert_to_start_end_date(start=start, end=end, format="%Y-%m-%d")

        payload: RequestPayload = {
            "url": constants.DSE_CLOSE_PRICE_URL,
            "key": f"close_price_{start}_{end}_{symbol}",
            "parser": "parse_historical_data",
            "data": {
                "startDate": start,
                "endDate": end,
                "inst": symbol,
                "archive": "data",
            },
            "method": "GET",
            "ttl": 3600,
        }

        # Fetch data using get_dataframe
        df = await self.get_dataframe(payload)

        if not df.empty and "date" in df.columns:
            df = df.set_index("date")
            df = df.sort_index(ascending=False)
        else:
            logger.warning("No close price data found")

        return df

"""Main BDFinance async client"""

from typing import Any

import structlog

from bdfinance.cache import CacheManager
from bdfinance.config import CacheConfig, ClientConfig
from bdfinance.http_client import AsyncHTTPClient
from bdfinance.repositories.market import MarketRepository
from bdfinance.repositories.news import NewsRepository
from bdfinance.repositories.trading import TradingRepository
from bdfinance.ticker import Ticker

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger()


class BaseClient:
    """Base client class"""

    pass


class BDStockClient(BaseClient):
    """
    High-performance async client for Bangladesh Stock Exchange data

    Usage:
    ```python
        async with BDStockClient() as client:
            ticker = client.ticker("ACI")
            quote = await ticker.quote()
            history = await ticker.history(period="1y")
            info = await ticker.info()
            fundamentals = await ticker.fundamentals()
    ```
    Attributes:
        trading: TradingRepository for trading data
        market: MarketRepository for market data
        news: NewsRepository for news data
    """

    def __init__(
        self,
        config: ClientConfig | None = None,
        cache_config: CacheConfig | None = None,
    ) -> None:
        """
        Initialize BDFinance client

        Args:
            config: Client configuration (optional)
            cache_config: Cache configuration (optional)
        """
        self.config = config or ClientConfig()
        self.cache_config = cache_config or CacheConfig()

        # Initialize HTTP client
        self._http_client = AsyncHTTPClient(self.config)

        # Initialize cache manager if enabled
        self._cache_manager: CacheManager | None = None
        if self.config.enable_cache:
            self._cache_manager = CacheManager(self.cache_config)

        # Initialize repositories
        self.trading = TradingRepository(self._http_client, self._cache_manager)
        self.market = MarketRepository(self._http_client, self._cache_manager)
        self.news = NewsRepository(self._http_client, self._cache_manager)

        logger.info(
            "BDFinance client initialized",
            cache_enabled=self.config.enable_cache,
            cache_backend=self.cache_config.backend if self.config.enable_cache else None,
        )

    def ticker(self, symbol: str) -> Ticker:
        """
        Create a Ticker instance for a specific symbol

        This provides a unified interface for accessing all data related to
        a specific stock symbol, similar to yfinance.

        Args:
            symbol: Stock symbol (e.g., "ACI", "BEXIMCO")

        Returns:
            Ticker instance

        Example:
            async with BDStockClient() as client:
                ticker = client.ticker("ACI")
                quote = await ticker.quote()
                history = await ticker.history("2024-01-01", "2024-12-31")
                info = await ticker.info()
        """
        return Ticker(
            symbol=symbol,
            http_client=self._http_client,
            cache_manager=self._cache_manager,
        )

    def tickers(self, symbols: list[str] | str) -> dict[str, Ticker]:
        """
        Create multiple Ticker instances for a list of symbols

        Args:
            symbols: List of stock symbols or space-separated string

        Returns:
            Dictionary of Ticker instances keyed by symbol
        """
        if isinstance(symbols, str):
            symbols = symbols.split(" ")

        return {symbol: self.ticker(symbol) for symbol in symbols}

    async def __aenter__(self) -> "BDStockClient":
        """Async context manager entry"""
        await self._http_client.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.close()

    async def close(self) -> None:
        """Close all connections and cleanup resources"""
        await self._http_client.close()
        if self._cache_manager:
            await self._cache_manager.close()
        logger.info("BDFinance client closed")

    async def clear_cache(self) -> None:
        """Clear all cached data"""
        if self._cache_manager:
            await self._cache_manager.clear()
            logger.info("Cache cleared")
        else:
            logger.warning("Cache not enabled")

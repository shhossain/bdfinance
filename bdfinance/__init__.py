"""
bdfinance - High-performance async Bangladesh stock market data library
"""

from bdfinance.client import BDStockClient
from bdfinance.config import CacheConfig, ClientConfig
from bdfinance.models.market import CompanyInfo, MarketDepth, MarketInfo
from bdfinance.models.news import AGMNews, News
from bdfinance.models.trading import CurrentTradeData
from bdfinance.ticker import Ticker

__version__ = "0.1.0"

__all__ = [
    "BDStockClient",
    "Ticker",
    "ClientConfig",
    "CacheConfig",
    "CurrentTradeData",
    "MarketInfo",
    "CompanyInfo",
    "MarketDepth",
    "AGMNews",
    "News",
]

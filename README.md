# bdfinance

High-performance async Python library for fetching Bangladesh stock market data from the Dhaka Stock Exchange (DSE).

Inspired by [yfinance](https://github.com/ranaroussi/yfinance), **bdfinance** provides a familiar `Ticker`-based API backed by async HTTP, automatic caching, structured logging, and Pydantic-validated models.

---

## Features

- **Async-first** — built on `httpx` with HTTP/2 and connection pooling
- **Ticker API** — unified interface per symbol: quote, history, info, depth, news, fundamentals
- **Batch processing** — fetch data for multiple symbols concurrently
- **Caching** — pluggable memory or Redis cache with configurable TTL
- **Pydantic models** — strongly typed, auto-validated data models
- **Retry & rate limiting** — exponential backoff with configurable rate limits
- **Structured logging** — powered by `structlog`
- **Treasury bonds** — coupon rates, approximate YTM calculations

---

## Installation

Requires **Python 3.12+**.

```bash
pip install bdfinance
```

Or install from source:

```bash
git clone https://github.com/your-username/bdfinance.git
cd bdfinance
pip install .
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `httpx[http2]` | Async HTTP client with HTTP/2 |
| `beautifulsoup4` + `lxml` | HTML parsing |
| `pandas` | DataFrames for historical/tabular data |
| `pydantic` + `pydantic-settings` | Data models and configuration |
| `tenacity` | Retry logic |
| `structlog` | Structured logging |
| `aiocache` + `msgpack` | Caching layer |

---

## Quick Start

```python
import asyncio
from bdfinance import BDStockClient

async def main():
    async with BDStockClient() as client:
        ticker = client.ticker("GP")

        # Current quote
        quote = await ticker.quote()
        print(f"{quote.symbol}: LTP {quote.ltp}, Change {quote.change}")

        # Historical data (returns pandas DataFrame)
        df = await ticker.history(period="1y")
        print(df.head())

        # Company information
        info = await ticker.info()
        print(info.basic_information.company_name)

        # Market depth
        depth = await ticker.depth()
        print(f"Buy: {depth.buy_price} | Sell: {depth.sell_price}")

        # Fundamentals (quote + info + PE combined)
        fundamentals = await ticker.fundamentals()

asyncio.run(main())
```

### Multiple Tickers

```python
async with BDStockClient() as client:
    tickers = client.tickers(["GP", "BEXIMCO", "ACI"])

    for symbol, ticker in tickers.items():
        quote = await ticker.quote()
        print(f"{symbol}: {quote.ltp}")
```

---

## Configuration

Both `ClientConfig` and `CacheConfig` use [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) and can be configured via constructor arguments or environment variables (prefixed with `BDFINANCE_` / `BDFINANCE_CACHE_`).

```python
from bdfinance import BDStockClient, ClientConfig, CacheConfig

config = ClientConfig(
    timeout=60.0,
    max_retries=5,
    rate_limit=20,
    enable_cache=True,
)

cache_config = CacheConfig(
    backend="memory",   # or "redis"
    ttl=600,            # seconds
)

async with BDStockClient(config=config, cache_config=cache_config) as client:
    ...
```

| Env Variable | Default | Description |
|---|---|---|
| `BDFINANCE_TIMEOUT` | `30.0` | Request timeout (seconds) |
| `BDFINANCE_MAX_RETRIES` | `3` | Max retry attempts |
| `BDFINANCE_RATE_LIMIT` | `10` | Max requests per second |
| `BDFINANCE_ENABLE_CACHE` | `true` | Enable response caching |
| `BDFINANCE_CACHE_BACKEND` | `memory` | `memory` or `redis` |
| `BDFINANCE_CACHE_TTL` | `300` | Cache TTL (seconds) |
| `BDFINANCE_CACHE_REDIS_URL` | `redis://localhost:6379/0` | Redis URL |

> See [docs/configuration.md](docs/configuration.md) for the full reference.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Client & Ticker](docs/client.md) | `BDStockClient` and `Ticker` API reference |
| [Configuration](docs/configuration.md) | `ClientConfig` and `CacheConfig` details |
| [Models](docs/models.md) | Pydantic data models (trading, market, news, company) |
| [Repositories](docs/repositories.md) | Low-level `TradingRepository`, `MarketRepository`, `NewsRepository` |
| [Caching](docs/caching.md) | Cache backends, key generation, TTL management |
| [Utilities](docs/utilities.md) | Data cleaners, date helpers, HTML parsers |

---

## Usage Examples

### Historical Data

```python
# By date range
df = await ticker.history(start="2024-01-01", end="2024-12-31")

# By period shorthand
df = await ticker.history(period="6mo")   # 6 months
df = await ticker.history(period="1y")    # 1 year
df = await ticker.history(period="30d")   # 30 days
```

### Market Data (via repositories)

```python
async with BDStockClient() as client:
    # Market overview
    overview = await client.market.get_market_overview(period="7d")

    # Latest P/E ratios
    pe = await client.market.get_latest_pe()

    # Top stocks / gainers / losers
    top = await client.market.get_top_stocks()
    gainers = await client.market.get_top_10_gainers()
    losers = await client.market.get_top_10_losers()

    # Sector listing
    sectors = await client.market.get_sector_listed()

    # Treasury bond yields
    bonds = await client.market.get_tbond_yields(tenor="10Y")
```

### News

```python
async with BDStockClient() as client:
    ticker = client.ticker("GP")

    # Company-specific news
    news = await ticker.news()

    # AGM news for this company
    agm = await ticker.agm_news()

    # All DSE news (via repository)
    all_news = await client.news.get_all_news()
```

### Cache Management

```python
async with BDStockClient() as client:
    # Clear all cached data
    await client.clear_cache()
```

---

## Project Structure

```
bdfinance/
├── __init__.py          # Public API exports
├── client.py            # BDStockClient entry point
├── ticker.py            # Unified Ticker interface
├── config.py            # ClientConfig / CacheConfig
├── constants.py         # DSE URLs and endpoints
├── http_client.py       # Async HTTP client
├── cache.py             # Cache backends (memory / redis)
├── parsers.py           # HTML parsing utilities
├── models/
│   ├── trading.py       # CurrentTradeData, BasicHistoricalData, ...
│   ├── market.py        # MarketInfo, MarketDepth, CompanyInfo, TBondInfo
│   ├── news.py          # AGMNews, News
│   └── company.py       # DSECompanyData and sub-models
├── repositories/
│   ├── base.py          # BaseRepository with get_data / get_dataframe
│   ├── trading.py       # TradingRepository
│   ├── market.py        # MarketRepository
│   └── news.py          # NewsRepository
└── utils/
    ├── common.py         # Dict helpers
    ├── data_cleaners.py  # clean_float, clean_int, clean_symbol, ...
    ├── date_helper.py    # Period parsing, date conversion
    └── parse_com_info.py # DSE company page parser
```

---

## License

MIT

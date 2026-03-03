# Repositories

> Back to [README](../README.md)

---

Repositories provide the low-level data access layer. They handle HTTP requests, HTML parsing, caching, and return either Pydantic models or pandas DataFrames.

Each repository extends `BaseRepository`, which provides two core methods:

- **`get_data(payload)`** — fetch, parse, and cache structured data (lists/dicts/models)
- **`get_dataframe(payload)`** — fetch, parse, and cache data as a `pd.DataFrame`

You can access repositories directly via the client:

```python
async with BDStockClient() as client:
    client.trading   # TradingRepository
    client.market    # MarketRepository
    client.news      # NewsRepository
```

---

## TradingRepository

Handles quotes, historical data, and symbol listing.

### `get_quote(symbol)`

Get current trading data. Supports three calling patterns:

```python
# Single symbol → CurrentTradeData | None
quote = await client.trading.get_quote("GP")

# Multiple symbols → dict[str, CurrentTradeData | None]
quotes = await client.trading.get_quote(["GP", "ACI"])

# All symbols → list[CurrentTradeData]
all_quotes = await client.trading.get_quote()
```

### `get_dsex_quote(symbol=None)`

Get DSEX index share data.

```python
# All DSEX shares
dsex_all = await client.trading.get_dsex_quote()

# Specific symbol in DSEX
dsex_gp = await client.trading.get_dsex_quote("GP")
```

### `get_trading_symbols() -> list[TradingSymbol]`

Get all actively trading symbols.

```python
symbols = await client.trading.get_trading_symbols()
for s in symbols:
    print(s.symbol)
```

### `get_history(start, end, period, symbol)`

Get historical price data. Supports single symbol, list of symbols, or the DSEX index.

```python
# Single symbol → DataFrame
df = await client.trading.get_history(symbol="GP", period="1y")

# Multiple symbols → dict[str, DataFrame]  (fetched concurrently)
dfs = await client.trading.get_history(symbol=["GP", "ACI"], period="6mo")

# DSEX index
dsex = await client.trading.get_history(symbol="DSEX", period="30d")

# All instruments (default)
all_df = await client.trading.get_history(start="2024-01-01", end="2024-06-30")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | `str \| datetime \| None` | `None` | Start date |
| `end` | `str \| datetime \| None` | `None` | End date |
| `period` | `str \| None` | `None` | Period shorthand |
| `symbol` | `str \| list[str]` | `"All Instrument"` | One or more symbols |

### `get_basic_historical(start, end, code, index)`

Get basic OHLCV historical data returned via `get_data` (non-DataFrame).

### `get_close_price(start, end, symbol)`

Get close price data as a DataFrame indexed by date.

```python
df = await client.trading.get_close_price("2024-01-01", "2024-12-31", "GP")
```

---

## MarketRepository

Handles company info, market overview, P/E ratios, sectors, top stocks, and treasury bonds.

### `get_company_info(symbol, summary=None) -> DSECompanyData | None`

Get comprehensive company information for a symbol. Optionally fetches a Wikipedia summary.

```python
info = await client.market.get_company_info("GP")
info_with_summary = await client.market.get_company_info("GP", summary=True)
```

### `get_company_summary(name) -> str | None`

Fetch a company summary from Wikipedia. Used internally by `get_company_info` when `summary=True`.

### `get_latest_pe() -> pd.DataFrame`

Get latest P/E ratios for all listed companies.

```python
pe_df = await client.market.get_latest_pe()
# Columns: Symbol, Close, YCP, P/E 1 through P/E 6
```

### `get_market_overview(start, end, period) -> pd.DataFrame`

Get market summary data over a date range.

```python
overview = await client.market.get_market_overview(period="7d")
```

### `get_market_depth(symbol) -> MarketDepth | None`

Get bid/ask depth for a symbol.

```python
depth = await client.market.get_market_depth("GP")
```

### `get_market_depth_batch(symbols) -> dict[str, list[MarketDepth]]`

Batch fetch market depth for multiple symbols concurrently.

```python
depths = await client.market.get_market_depth_batch(["GP", "ACI", "BEXIMCO"])
```

### `get_sector_listed() -> pd.DataFrame`

Get list of all sectors with sector codes.

```python
sectors = await client.market.get_sector_listed()
# Columns: Sector, Code
```

### `get_latest_share_price_by_sector(sector) -> pd.DataFrame`

Get latest share prices for a sector. Accepts either a sector name or sector code.

```python
df = await client.market.get_latest_share_price_by_sector("Bank")
# or by code
df = await client.market.get_latest_share_price_by_sector("3")
```

### `get_top_stocks() -> pd.DataFrame`

Get top performing stocks.

### `get_top_10_gainers() -> pd.DataFrame`

Get top 10 daily gainers.

### `get_top_10_losers() -> pd.DataFrame`

Get top 10 daily losers.

### `get_top_10(type) -> pd.DataFrame`

Get top 10 gainers or losers.

```python
gainers = await client.market.get_top_10("gainers")
losers = await client.market.get_top_10("losers")
```

### `get_tbond_yields(tenor="10Y") -> list[TBondInfo]`

Get treasury bond data including coupon rates and approximate YTM.

```python
bonds = await client.market.get_tbond_yields(tenor="10Y")
for b in bonds:
    print(f"{b.symbol}: coupon={b.coupon_rate}%, YTM≈{b.approx_ytm}%")

# All tenors
all_bonds = await client.market.get_tbond_yields(tenor="all")
```

| Tenor | Description |
|-------|-------------|
| `"2Y"` | 2-year bonds |
| `"5Y"` | 5-year bonds |
| `"10Y"` | 10-year bonds (default) |
| `"15Y"` | 15-year bonds |
| `"20Y"` | 20-year bonds |
| `"all"` | All tenors |

---

## NewsRepository

Handles AGM/EGM news and general DSE news.

### `get_agm_news() -> list[AGMNews]`

Get all AGM/EGM news.

```python
agm_list = await client.news.get_agm_news()
for agm in agm_list:
    print(f"{agm.company} — {agm.dividend} — {agm.agm_date}")
```

### `get_all_news(symbol=None) -> list[News]`

Get general news. Optionally filter by symbol.

```python
# All news
all_news = await client.news.get_all_news()

# Company-specific news
gp_news = await client.news.get_all_news(symbol="GP")
```

---

## BaseRepository

All repositories inherit from `BaseRepository`, which provides:

### `get_data(payload: RequestPayload) -> Any | None`

Fetch data with caching. The `RequestPayload` dict contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | `str` | Yes | Endpoint URL (relative to DSE base) |
| `key` | `str` | Yes | Cache key identifier |
| `parser` | `str \| Callable` | Yes | Parser method name or callable |
| `data` | `dict \| None` | No | Request params/data |
| `method` | `str \| None` | No | `"GET"` (default) or `"POST"` |
| `ttl` | `int \| None` | No | Cache TTL override (default: 3600) |

### `get_dataframe(payload: RequestPayload) -> pd.DataFrame`

Same as `get_data` but wraps the result in a `pd.DataFrame`.

---

> **See also:** [Client & Ticker](client.md) · [Models](models.md) · [Caching](caching.md)

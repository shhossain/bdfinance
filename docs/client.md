# Client & Ticker API

> Back to [README](../README.md)

---

## BDStockClient

`BDStockClient` is the main entry point for all interactions with the library. It manages HTTP connections, caching, and exposes both a high-level **Ticker** interface and low-level **repository** access.

### Constructor

```python
from bdfinance import BDStockClient, ClientConfig, CacheConfig

client = BDStockClient(
    config: ClientConfig | None = None,
    cache_config: CacheConfig | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `ClientConfig \| None` | `None` | HTTP client settings (timeout, retries, rate limit, proxy, etc.) |
| `cache_config` | `CacheConfig \| None` | `None` | Cache backend and TTL settings |

When `None`, default configurations are used. See [Configuration](configuration.md) for details.

### Context Manager (recommended)

```python
async with BDStockClient() as client:
    # connections are opened
    ...
# connections are closed automatically
```

The context manager calls `start()` on entry and `close()` on exit.

### Methods

#### `ticker(symbol: str) -> Ticker`

Create a [`Ticker`](#ticker) instance for a single stock symbol.

```python
ticker = client.ticker("GP")
```

#### `tickers(symbols: list[str] | str) -> dict[str, Ticker]`

Create multiple `Ticker` instances. Accepts a list or space-separated string.

```python
tickers = client.tickers(["GP", "ACI", "BEXIMCO"])
# or
tickers = client.tickers("GP ACI BEXIMCO")
```

Returns a `dict[str, Ticker]` keyed by symbol.

#### `close() -> None`

Close all HTTP connections and cache backends. Called automatically when using the context manager.

#### `clear_cache() -> None`

Clear all cached data. Logs a warning if caching is disabled.

### Repository Access

The client exposes three repositories as attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `client.trading` | [`TradingRepository`](repositories.md#tradingrepository) | Quotes, history, symbols |
| `client.market` | [`MarketRepository`](repositories.md#marketrepository) | Company info, PE, sectors, bonds |
| `client.news` | [`NewsRepository`](repositories.md#newsrepository) | AGM news, general news |

---

## Ticker

`Ticker` provides a unified, symbol-scoped interface for all data related to a single stock. It wraps the three repositories internally.

### Creating a Ticker

Always create tickers through the client:

```python
async with BDStockClient() as client:
    ticker = client.ticker("GP")
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `symbol` | `str` | Normalized (uppercased, stripped) stock symbol |

### Methods

#### `quote() -> CurrentTradeData | None`

Get the current trading quote for this symbol.

```python
quote = await ticker.quote()
print(quote.ltp)       # Last traded price
print(quote.change)    # Price change
print(quote.volume)    # Volume traded
```

Returns a [`CurrentTradeData`](models.md#currenttradedata) model or `None` if the symbol is not found.

#### `validate_symbol() -> bool`

Check if the symbol exists on the DSE.

```python
is_valid = await ticker.validate_symbol()
```

#### `history(start, end, period) -> pd.DataFrame`

Get historical trading data. Returns a pandas DataFrame with columns: `Date`, `Symbol`, `LTP`, `High`, `Low`, `Open`, `Close`, `YCP`, `Trade`, `Value`, `Volume`.

```python
# By explicit dates
df = await ticker.history(start="2024-01-01", end="2024-12-31")

# By period shorthand
df = await ticker.history(period="1y")    # 1 year
df = await ticker.history(period="6mo")   # 6 months
df = await ticker.history(period="30d")   # 30 days (default)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | `str \| datetime \| None` | `None` | Start date (`YYYY-MM-DD` or datetime) |
| `end` | `str \| datetime \| None` | `None` | End date (`YYYY-MM-DD` or datetime) |
| `period` | `str \| timedelta \| None` | `None` | Period shorthand (`30d`, `6mo`, `1y`, etc.) |

If neither `start`/`end` nor `period` is provided, defaults to the last **30 days**.

#### `info(summary: bool | None = None) -> DSECompanyData | None`

Get comprehensive company information.

```python
info = await ticker.info()
print(info.basic_information.company_name)
print(info.market_information.last_trading_price)
print(info.financial_performance.statements)

# Include Wikipedia summary
info = await ticker.info(summary=True)
print(info.basic_information.summary)
```

Returns a [`DSECompanyData`](models.md#dsecompanydata) model. See [Models — Company](models.md#company-models) for the full structure.

#### `depth() -> MarketDepth | None`

Get market depth (bid/ask) data.

```python
depth = await ticker.depth()
print(f"Buy: {depth.buy_price} x {depth.buy_volume}")
print(f"Sell: {depth.sell_price} x {depth.sell_volume}")
```

Returns a [`MarketDepth`](models.md#marketdepth) model.

#### `news() -> list[News]`

Get news items related to this company.

```python
news_list = await ticker.news()
for item in news_list:
    print(f"[{item.post_date}] {item.news_title}")
```

Returns a list of [`News`](models.md#news) models.

#### `agm_news() -> list[AGMNews]`

Get AGM/EGM news filtered for this company.

```python
agm_list = await ticker.agm_news()
for agm in agm_list:
    print(f"{agm.company} — Dividend: {agm.dividend}, Date: {agm.agm_date}")
```

Returns a list of [`AGMNews`](models.md#agmnews) models.

#### `fundamentals() -> dict[str, Any]`

Get combined fundamental data: quote, company info, and P/E ratio. All three are fetched concurrently.

```python
fundamentals = await ticker.fundamentals()
print(fundamentals["symbol"])        # str
print(fundamentals["quote"])         # CurrentTradeData | None
print(fundamentals["company_info"])  # DSECompanyData | None
print(fundamentals["pe_data"])       # dict | None
```

Returns a dictionary:

| Key | Type | Description |
|-----|------|-------------|
| `symbol` | `str` | The stock symbol |
| `quote` | `CurrentTradeData \| None` | Current quote |
| `company_info` | `DSECompanyData \| None` | Company info |
| `pe_data` | `dict \| None` | P/E ratio row for this symbol |

---

> **See also:** [Models](models.md) · [Repositories](repositories.md) · [Configuration](configuration.md)

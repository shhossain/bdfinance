# Utilities

> Back to [README](../README.md)

---

The `bdfinance.utils` package contains helper functions for data cleaning, date handling, and HTML parsing. These are used internally by parsers and repositories but are also available for direct use.

---

## Data Cleaners

Module: `bdfinance.utils.data_cleaners`

Centralized functions for cleaning raw string values from DSE HTML pages.

### `clean_text(value) -> str`

Strip whitespace from any value, converting to string first.

```python
clean_text("  hello  ")  # "hello"
clean_text(None)          # ""
```

### `clean_float(value, default=0.0) -> float`

Convert to float, handling commas, `"n/a"`, dashes, and empty strings.

```python
clean_float("1,234.56")  # 1234.56
clean_float("n/a")       # 0.0
clean_float("-")          # 0.0
clean_float(42)           # 42.0
```

### `clean_int(value, default=0) -> int`

Convert to int with the same edge-case handling as `clean_float`.

```python
clean_int("1,234")  # 1234
clean_int("n/a")    # 0
clean_int(3.7)      # 3
```

### `clean_percent(value) -> float`

Strip `%` sign and convert to float.

```python
clean_percent("15.5%")  # 15.5
clean_percent(10)       # 10.0
```

### `clean_symbol(value) -> str`

Uppercase and strip a stock symbol.

```python
clean_symbol("  gp  ")  # "GP"
```

### `clean_date(value, format="%Y-%m-%d") -> datetime`

Parse a date string using the given format.

```python
clean_date("2024-01-15")                        # datetime(2024, 1, 15)
clean_date("15-01-2024", format="%d-%m-%Y")      # datetime(2024, 1, 15)
```

### `parse_market_value(value) -> float`

Parse market values with unit suffixes (`mn`, `bn`, `cr`) and return value in millions.

```python
parse_market_value("1,234.56 mn")  # 1234.56
parse_market_value("1.5 bn")      # 1500.0
parse_market_value("100 cr")      # 1000.0
```

### `extract_tenor_from_symbol(symbol) -> str`

Extract bond tenor from a treasury bond symbol.

```python
extract_tenor_from_symbol("TB10Y0634")  # "10Y"
extract_tenor_from_symbol("TB5Y0123")   # "5Y"
```

### `compute_approx_ytm(coupon, face, price, maturity_date_str) -> float | None`

Compute approximate yield-to-maturity using the formula:

$$YTM \approx \frac{C + \frac{F - P}{n}}{\frac{F + P}{2}} \times 100$$

Where $C$ = annual coupon, $F$ = face value, $P$ = market price, $n$ = years to maturity.

```python
compute_approx_ytm(coupon=7.5, face=100, price=98.5, maturity_date_str="2030-06-15")
# Returns approximate YTM as percentage
```

---

## Date Helpers

Module: `bdfinance.utils.date_helper`

### `period_parsing(period) -> timedelta`

Convert a period shorthand string to a `timedelta`.

| Input | Result |
|-------|--------|
| `"30d"` | `timedelta(days=30)` |
| `"6mo"` | `timedelta(days=180)` |
| `"1y"` | `timedelta(days=365)` |
| `"2y"` | `timedelta(days=730)` |

### `convert_to_start_end_date(start, end, period, default_period, format) -> tuple[str, str]`

Resolve start/end dates from various input combinations. Used throughout repositories and the Ticker class.

```python
start, end = convert_to_start_end_date(
    start=None,
    end=None,
    period="1y",
    format="%Y-%m-%d",
)
# Returns ("2025-03-03", "2026-03-03") — relative to current date
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | `str \| datetime \| None` | — | Start date |
| `end` | `str \| datetime \| None` | — | End date |
| `period` | `str \| timedelta \| None` | `None` | Period shorthand |
| `default_period` | `str` | `"30d"` | Fallback period if nothing provided |
| `format` | `str` | `"%Y-%m-%d"` | Output date format |

---

## Common Helpers

Module: `bdfinance.utils.common`

### `make_lower_case(s) -> str`

Convert a string to lowercase with spaces and hyphens replaced by underscores.

```python
make_lower_case("Last Trading Price")  # "last_trading_price"
```

### `convert_dict_keys_to_lower(d) -> dict`

Lowercase all keys in a dictionary using `make_lower_case`.

```python
convert_dict_keys_to_lower({"Symbol": "GP", "Last Price": 300})
# {"symbol": "GP", "last_price": 300}
```

### `adapt_dict_values(d) -> Any`

Recursively convert string values in a dict/list to appropriate Python types (int, float, bool).

```python
adapt_dict_values({"price": "123.45", "count": "100", "active": "true"})
# {"price": 123.45, "count": 100, "active": True}
```

---

## Company Info Parser

Module: `bdfinance.utils.parse_com_info`

This module contains the `parse_dse_company_data()` function and its helpers, which parse the full DSE company information page HTML into a `DSECompanyData` Pydantic model.

### Key Functions

| Function | Description |
|----------|-------------|
| `parse_dse_company_data(soup)` | Main entry point — parses BeautifulSoup object into `DSECompanyData` |
| `parse_date(date_str)` | Flexible date parser using `dateutil` |
| `parse_number(value)` | Parse numeric strings with commas |
| `parse_percentage(value)` | Parse percentage strings |
| `parse_company_basic_info(table, h2)` | Extract company name and trading codes |
| `parse_market_information(table, h2)` | Parse market information section |
| `parse_basic_information(table)` | Parse basic company details, dividends, right issues |

---

## HTML Parsers

Module: `bdfinance.parsers`

The `HTMLParser` class contains static methods for parsing various DSE HTML pages. These are called by repositories via the `parser` field in `RequestPayload`.

### Parser Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `parse_current_trade_data(html)` | `list[dict]` | Current trade data table |
| `parse_historical_data(html)` | `list[dict]` | Historical OHLCV data |
| `parse_index_data(html)` | `list[dict]` | DSEX market summary data |
| `parse_market_info(html)` | `list[dict]` | Market information table |
| `parse_latest_pe(html)` | `list[dict]` | Latest P/E ratios |
| `parse_market_depth(html)` | `list[dict]` | Market depth (bid/ask) |
| `parse_agm_news(html)` | `list[dict]` | AGM/EGM news |
| `parse_news(html)` | `list[dict]` | General news items |
| `parse_company_info(html)` | `DSECompanyData` | Full company information |
| `parse_sector_list(html)` | `list[dict]` | Sector listing |
| `parse_latest_share_price(html)` | `list[dict]` | Latest share prices |
| `parse_top_stocks(html)` | `list[dict]` | Top stocks |
| `parse_top_10(html)` | `list[dict]` | Top 10 gainers/losers |
| `parse_tbond_info(html)` | `dict` | Treasury bond details |
| `parse_table_to_dicts(html, ...)` | `list[dict]` | Generic table parser |
| `parse_simple_table(table, ...)` | `list[dict]` | Configurable table parser with mappings |
| `parse_table_rows(trs)` | `list[dict]` | Key-value pair table rows |

### `parse_simple_table` — Advanced Options

This is the most flexible parser, used by several higher-level methods:

```python
HTMLParser.parse_simple_table(
    table,                      # BeautifulSoup Tag
    add_links=True,             # Extract <a> href as {col}_Link
    mappings={"Old": "New"},    # Rename columns
    transform_keys=func,        # Transform all key names
    transform_values={"col": func},  # Transform specific column values
    remove_cols=["#"],          # Remove columns
)
```

---

> **See also:** [Models](models.md) · [Repositories](repositories.md)

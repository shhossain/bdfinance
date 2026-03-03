# Data Models

> Back to [README](../README.md)

---

All models are [Pydantic](https://docs.pydantic.dev/) `BaseModel` subclasses with built-in validation and serialization. Raw string values from DSE HTML pages are automatically cleaned (commas removed, `"n/a"` → default, etc.) via field validators.

---

## Trading Models

Defined in `bdfinance.models.trading`.

### CurrentTradeData

Current (live) trading data for a stock symbol.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Stock symbol (uppercase) |
| `ltp` | `float` | Last traded price |
| `high` | `float` | Day high |
| `low` | `float` | Day low |
| `close` | `float` | Closing price |
| `ycp` | `float` | Yesterday's closing price |
| `change` | `float` | Price change |
| `trade` | `int` | Number of trades |
| `value` | `float` | Total value traded |
| `volume` | `int` | Total volume traded |

### BasicHistoricalData

Simplified OHLCV historical data point.

| Field | Type | Description |
|-------|------|-------------|
| `date` | `datetime` | Trading date |
| `open` | `float` | Opening price |
| `high` | `float` | Day high |
| `low` | `float` | Day low |
| `close` | `float` | Closing price |
| `volume` | `int` | Total volume |

### ClosePriceData

Close price record with yesterday's close for comparison.

| Field | Type | Description |
|-------|------|-------------|
| `date` | `datetime` | Trading date |
| `symbol` | `str` | Stock symbol |
| `close` | `float` | Closing price |
| `ycp` | `float` | Yesterday's closing price |

### TradingSymbol

Minimal model holding a single trading symbol.

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | `str` | Stock symbol |

---

## Market Models

Defined in `bdfinance.models.market`.

### MarketInfo

Daily market summary data.

| Field | Type | Description |
|-------|------|-------------|
| `date` | `str` | Date |
| `total_trade` | `int` | Total number of trades |
| `total_volume` | `int` | Total volume |
| `total_value` | `float` | Total value in millions |
| `total_market_cap` | `float` | Total market cap in millions |
| `dsex_index` | `float` | DSEX index value |
| `dses_index` | `float` | DSES index value |
| `ds30_index` | `float` | DS30 index value |
| `dgen_index` | `float` | DGEN index value |

### MarketDepth

Bid/ask (market depth) data.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `buy_price` | `float` | `0.0` | Buy price |
| `buy_volume` | `int` | `0` | Buy volume |
| `sell_price` | `float` | `0.0` | Sell price |
| `sell_volume` | `int` | `0` | Sell volume |

### CompanyInfo

Wrapper model for raw company information dictionary.

| Field | Type | Description |
|-------|------|-------------|
| `data` | `dict` | Company information data |

### TBondInfo

Treasury bond information with yield data.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `symbol` | `str` | — | Trading symbol (e.g. `TB10Y0634`) |
| `tenor` | `str` | — | Bond tenor (`2Y`, `5Y`, `10Y`, `15Y`, `20Y`) |
| `coupon_rate` | `float` | — | Coupon rate (%) |
| `coupon_frequency` | `int` | `2` | Coupon payments per year |
| `face_value` | `float` | `100.0` | Face/par value |
| `issue_date` | `str \| None` | `None` | Issue date |
| `maturity_date` | `str \| None` | `None` | Maturity date |
| `close_price` | `float` | `0.0` | Last close price |
| `approx_ytm` | `float \| None` | `None` | Approximate yield to maturity (%) |

---

## News Models

Defined in `bdfinance.models.news`.

### News

General news item.

| Field | Type | Description |
|-------|------|-------------|
| `news_title` | `str \| None` | News title |
| `news` | `str \| None` | News body text |
| `post_date` | `str \| None` | Post date |

### AGMNews

Annual General Meeting / Extraordinary General Meeting news.

| Field | Type | Description |
|-------|------|-------------|
| `company` | `str` | Company name |
| `year_end` | `str` | Year end date |
| `dividend` | `str` | Dividend information |
| `agm_date` | `str` | AGM/EGM date |
| `record_date` | `str` | Record date |
| `venue` | `str` | Venue |
| `time` | `str` | Time |

---

## Company Models

Defined in `bdfinance.models.company`. These models represent the comprehensive data returned by `ticker.info()`.

### DSECompanyData

Top-level container for all company data sections. Returned by `ticker.info()` and `MarketRepository.get_company_info()`.

| Field | Type | Description |
|-------|------|-------------|
| `basic_information` | `BasicInformation` | Company identifiers, capital, dividends |
| `market_information` | `MarketInformation` | Current market data |
| `financial_performance` | `FinancialPerformance` | Audited financial statements |
| `interim_financial_performance` | `InterimFinancialPerformance` | Quarterly interim data |
| `pe_ratios` | `PERatios` | P/E ratios (audited + unaudited) |
| `other_information` | `OtherInformation` | Listing info, shareholding |
| `corporate_performance` | `CorporatePerformance` | Operational status, loans, ratings |
| `address` | `CompanyAddress` | Head office, contacts |

### BasicInformation

| Field | Type | Description |
|-------|------|-------------|
| `company_name` | `str` | Company name |
| `trading_code` | `str` | Trading code |
| `scrip_code` | `str` | Scrip code |
| `authorized_capital_mn` | `float \| None` | Authorized capital (mn) |
| `paid_up_capital_mn` | `float \| None` | Paid-up capital (mn) |
| `face_value` | `float \| None` | Face/par value |
| `total_outstanding_securities` | `float \| None` | Outstanding share count |
| `market_lot` | `float \| None` | Market lot |
| `reserve_surplus_mn` | `float \| None` | Reserve & surplus (mn) |
| `oci_mn` | `float \| None` | OCI (mn) |
| `debut_trading_date` | `datetime \| None` | Debut trading date |
| `last_agm_date` | `datetime \| None` | Last AGM date |
| `financial_year_ended` | `datetime \| None` | Financial year end |
| `instrument_type` | `str \| None` | Instrument type |
| `sector` | `str \| None` | Sector |
| `year_end` | `str \| None` | Year end |
| `cash_dividends` | `list[DividendRecord]` | Cash dividend history |
| `bonus_issues` | `list[DividendRecord]` | Bonus issue history |
| `right_issue` | `list[RightIssueRecord]` | Right issue history |
| `summary` | `str \| None` | Wikipedia summary (if requested) |

### MarketInformation

| Field | Type | Description |
|-------|------|-------------|
| `last_trading_price` | `float \| None` | LTP |
| `closing_price` | `float \| None` | Closing price |
| `last_updated` | `datetime \| None` | Last update timestamp |
| `opening_price` | `float \| None` | Opening price |
| `adjusted_opening_price` | `float \| None` | Adjusted opening price |
| `yesterday_closing_price` | `float \| None` | Yesterday's closing price |
| `days_range` | `str \| None` | Day's price range |
| `days_value_mn` | `float \| None` | Day's value (mn) |
| `weeks_52_range` | `str \| None` | 52-week range |
| `days_volume` | `float \| None` | Day's volume |
| `days_trade` | `int \| None` | Day's trade count |
| `market_cap_mn` | `float \| None` | Market cap (mn) |
| `change_value` | `float \| None` | Price change |
| `change_percentage` | `float \| None` | Change percentage |

### FinancialPerformance

| Field | Type | Description |
|-------|------|-------------|
| `statements` | `list[FinancialPerformanceAudited]` | Audited annual statements |
| `financial_statement_url` | `str \| None` | Link to financial statement |
| `price_sensitive_info_url` | `str \| None` | Link to price-sensitive info |
| `audited_by` | `str` | Auditor name |

### FinancialPerformanceAudited

Annual audited financial statement. Contains EPS (basic/diluted/restated), NAV, profit, P/E ratios, and dividend info. Each field is `float | None` with year as `int`.

### InterimFinancialPerformance

Quarterly interim data with `InterimEPS` entries for Q1, Q2, half-yearly, Q3, nine-months, and annual.

### PERatios

| Field | Type | Description |
|-------|------|-------------|
| `unaudited` | `list[PERatioEntry]` | P/E from unaudited statements |
| `audited` | `list[PERatioEntry]` | P/E from audited statements |

Each `PERatioEntry` has `date: datetime`, `metric: str`, `value: float`.

### OtherInformation

| Field | Type | Description |
|-------|------|-------------|
| `listing_year` | `int \| None` | Year of listing |
| `market_category` | `str \| None` | Market category |
| `electronic_share` | `str \| None` | Electronic share status |
| `remarks` | `str \| None` | Remarks |
| `shareholding` | `list[ShareholdingEntry]` | Shareholding breakdown |

### CorporatePerformance

| Field | Type | Description |
|-------|------|-------------|
| `operational_status` | `str \| None` | Operational status |
| `short_term_loan_mn` | `float \| None` | Short-term loan (mn) |
| `long_term_loan_mn` | `float \| None` | Long-term loan (mn) |
| `latest_dividend` | `str \| None` | Latest dividend info |
| `credit_rating_short_term` | `str \| None` | Short-term credit rating |
| `credit_rating_long_term` | `str \| None` | Long-term credit rating |

### CompanyAddress

| Field | Type | Description |
|-------|------|-------------|
| `head_office` | `str \| None` | Head office address |
| `phone` | `str \| None` | Phone number |
| `email` | `str \| None` | Email |
| `website` | `str \| None` | Website URL |
| `company_secretary` | `str \| None` | Company secretary name |
| `factory` | `str \| None` | Factory address |
| `fax` | `str \| None` | Fax number |

### Supporting Models

| Model | Description |
|-------|-------------|
| `DividendRecord` | `percentage: float`, `label: str \| None`, `year: int` |
| `RightIssueRecord` | `ratio: str`, `price: str \| None`, `year: int` |
| `ShortInfo` | `company_name`, `trading_code`, `scrip_code` |
| `ShareholdingEntry` | `date`, `sponsor_director`, `govt`, `institute`, `foreign`, `public` (all `float \| None`) |
| `InterimEPS` | `eps_basic`, `eps_diluted`, `eps_continuing_basic`, `eps_continuing_diluted`, `market_price` |

---

> **See also:** [Client & Ticker](client.md) · [Repositories](repositories.md)

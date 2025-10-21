"""Tests for trading repository"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from bdfinance.models.trading import CurrentTradeData, TradingSymbol


@pytest.mark.asyncio
async def test_get_quote_single(client, sample_symbol):
    """Test fetching current trade data for a single symbol"""
    data = await client.trading.get_quote(sample_symbol)

    assert data is not None
    assert isinstance(data, CurrentTradeData)
    assert data.symbol == sample_symbol
    assert isinstance(data.ltp, (int, float))
    assert data.ltp >= 0
    assert isinstance(data.volume, int)
    assert data.volume >= 0


@pytest.mark.asyncio
async def test_get_quote_multiple(client):
    """Test fetching current trade data for multiple symbols"""
    symbols = ["ACI", "GP", "BRACBANK"]
    data = await client.trading.get_quote(symbols)

    assert isinstance(data, dict)
    assert len(data) == len(symbols)
    for symbol in symbols:
        assert symbol in data
        if data[symbol] is not None:
            assert isinstance(data[symbol], CurrentTradeData)
            assert data[symbol].symbol == symbol


@pytest.mark.asyncio
async def test_get_quote_all(client):
    """Test fetching all current trade data"""
    data = await client.trading.get_quote()

    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, CurrentTradeData) for item in data)
    # Check that we have a good variety of symbols
    assert len(data) > 100


@pytest.mark.asyncio
async def test_get_quote_nonexistent(client):
    """Test fetching quote for nonexistent symbol"""
    data = await client.trading.get_quote("NONEXISTENT123")

    assert data is None


@pytest.mark.asyncio
async def test_get_dsex_quote_all(client):
    """Test fetching DSEX data"""
    data = await client.trading.get_dsex_quote()

    assert isinstance(data, list)
    # May be empty if endpoint format changed
    if len(data) > 0:
        assert all(isinstance(item, CurrentTradeData) for item in data)


@pytest.mark.asyncio
async def test_get_dsex_quote_single(client):
    """Test fetching DSEX data for single symbol"""
    data = await client.trading.get_dsex_quote("DSEX")

    if data is not None:
        assert isinstance(data, CurrentTradeData)
        assert data.symbol == "DSEX"


@pytest.mark.asyncio
async def test_get_trading_symbols(client):
    """Test fetching all trading symbols"""
    symbols = await client.trading.get_trading_symbols()

    assert isinstance(symbols, list)
    assert len(symbols) > 0
    assert all(isinstance(s, TradingSymbol) for s in symbols)
    assert all(hasattr(s, "symbol") for s in symbols)
    # Check some known symbols are present
    symbol_list = [s.symbol for s in symbols]
    assert "ACI" in symbol_list
    assert "GP" in symbol_list


@pytest.mark.asyncio
async def test_get_history_single_symbol_period(client, sample_symbol):
    """Test fetching historical data for single symbol with period"""
    df = await client.trading.get_history(period="7d", symbol=sample_symbol)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Symbol" in df.columns or "symbol" in df.columns.str.lower()
    # Should have OHLCV data
    cols_lower = [c.lower() for c in df.columns]
    assert any("ltp" in c or "close" in c for c in cols_lower)
    assert any("volume" in c for c in cols_lower)


@pytest.mark.asyncio
async def test_get_history_single_symbol_dates(client, sample_symbol):
    """Test fetching historical data for single symbol with date range"""
    end = datetime.now()
    start = end - timedelta(days=30)
    
    df = await client.trading.get_history(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        symbol=sample_symbol
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.asyncio
async def test_get_history_multiple_symbols(client):
    """Test fetching historical data for multiple symbols"""
    symbols = ["ACI", "GP"]
    result = await client.trading.get_history(period="7d", symbol=symbols)

    assert isinstance(result, dict)
    assert len(result) == len(symbols)
    for symbol in symbols:
        assert symbol in result
        assert isinstance(result[symbol], pd.DataFrame)


@pytest.mark.asyncio
async def test_get_history_all_instruments(client):
    """Test fetching historical data for all instruments"""
    df = await client.trading.get_history(period="1d")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Should have multiple symbols
    if "Symbol" in df.columns:
        assert len(df["Symbol"].unique()) > 1


@pytest.mark.asyncio
async def test_get_history_dsex(client):
    """Test fetching DSEX index historical data"""
    df = await client.trading.get_history(period="7d", symbol="DSEX")

    assert isinstance(df, pd.DataFrame)
    # May be empty or have data


@pytest.mark.asyncio
async def test_get_basic_historical(client, sample_symbol):
    """Test fetching basic historical OHLCV data"""
    end = datetime.now()
    start = end - timedelta(days=30)
    
    df = await client.trading.get_basic_historical(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        code=sample_symbol
    )

    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        # Should have basic OHLCV columns
        cols_lower = [c.lower() for c in df.columns]
        assert "date" in cols_lower
        assert "open" in cols_lower
        assert "high" in cols_lower
        assert "low" in cols_lower
        assert "close" in cols_lower
        assert "volume" in cols_lower


@pytest.mark.asyncio
async def test_get_basic_historical_with_index(client, sample_symbol):
    """Test fetching basic historical data with date as index"""
    end = datetime.now()
    start = end - timedelta(days=30)
    
    df = await client.trading.get_basic_historical(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        code=sample_symbol,
        index=True
    )

    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        # Index should be date
        assert df.index.name == "date" or isinstance(df.index[0], str)


@pytest.mark.asyncio
async def test_get_close_price(client, sample_symbol):
    """Test fetching close price data"""
    end = datetime.now()
    start = end - timedelta(days=30)
    
    df = await client.trading.get_close_price(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        symbol=sample_symbol
    )

    assert isinstance(df, pd.DataFrame)
    # May be empty or have data
    if not df.empty:
        index_name = str(df.index.name or "")
        cols_lower = [str(c).lower() for c in df.columns]
        assert "date" in index_name.lower() or "date" in cols_lower


@pytest.mark.asyncio
async def test_cache_usage(client):
    """Test that caching works for quote data"""
    import time

    # First call (cache miss)
    start = time.time()
    data1 = await client.trading.get_quote("GP")
    time1 = time.time() - start

    # Second call (cache hit)
    start = time.time()
    data2 = await client.trading.get_quote("GP")
    time2 = time.time() - start

    # Cache hit should be significantly faster
    assert time2 < time1 * 0.5  # At least 50% faster
    assert data1 == data2


@pytest.mark.asyncio
async def test_batch_processing(client):
    """Test batch processing of multiple symbols"""
    symbols = ["ACI", "GP", "BRACBANK", "SQURPHARMA"]
    
    # Batch fetch historical data
    result = await client.trading.get_history(period="7d", symbol=symbols)

    assert isinstance(result, dict)
    assert len(result) == len(symbols)
    for symbol in symbols:
        assert symbol in result
        assert isinstance(result[symbol], pd.DataFrame)

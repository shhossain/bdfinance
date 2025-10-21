"""Tests for market repository"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from bdfinance.models.market import MarketDepth
from bdfinance.utils.parse_com_info import DSECompanyData


@pytest.mark.asyncio
async def test_get_company_info(client, sample_symbol):
    """Test fetching company information"""
    data = await client.market.get_company_info(sample_symbol)

    assert data is not None
    assert isinstance(data, DSECompanyData)
    assert data.basic_information is not None
    assert data.basic_information.trading_code is not None
    assert data.market_information is not None
    assert data.address is not None


@pytest.mark.asyncio
async def test_get_company_info_with_summary(client):
    """Test fetching company information with Wikipedia summary"""
    data = await client.market.get_company_info("GP", summary=True)

    assert data is not None
    assert isinstance(data, DSECompanyData)
    assert data.basic_information is not None
    # Summary might be None if Wikipedia fetch fails
    # Just check that the call doesn't error


@pytest.mark.asyncio
async def test_get_company_info_multiple_symbols(client, sample_symbols):
    """Test fetching company info for multiple symbols"""
    for symbol in sample_symbols[:3]:  # Test first 3 symbols
        data = await client.market.get_company_info(symbol)
        assert data is not None
        assert isinstance(data, DSECompanyData)


@pytest.mark.asyncio
async def test_get_company_summary(client):
    """Test fetching company summary from Wikipedia"""
    summary = await client.market.get_company_summary("Grameenphone Ltd.")

    # Summary may be None if not found
    if summary is not None:
        assert isinstance(summary, str)
        assert len(summary) > 0


@pytest.mark.asyncio
async def test_get_latest_pe(client):
    """Test fetching latest P/E ratios"""
    try:
        df = await client.market.get_latest_pe()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        cols_lower = [str(c).lower() for c in df.columns]
        assert any("symbol" in c for c in cols_lower)
        assert any("p/e" in c for c in cols_lower)
    except Exception as e:
        # Network issues may occur
        if "ConnectError" in str(type(e).__name__) or "502" in str(e):
            pytest.skip(f"Network error accessing DSE: {e}")
        raise


@pytest.mark.asyncio
async def test_get_market_overview_with_period(client):
    """Test fetching market overview with period"""
    df = await client.market.get_market_overview(period="7d")

    assert isinstance(df, pd.DataFrame)
    # May be empty or have data


@pytest.mark.asyncio
async def test_get_market_overview_with_dates(client):
    """Test fetching market overview with date range"""
    end = datetime.now()
    start = end - timedelta(days=30)
    
    df = await client.market.get_market_overview(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d")
    )

    assert isinstance(df, pd.DataFrame)
    # May be empty or have data


@pytest.mark.asyncio
async def test_get_market_depth(client, sample_symbol):
    """Test fetching market depth for a symbol"""
    depth = await client.market.get_market_depth(sample_symbol)

    # May be None if no data
    if depth is not None:
        assert isinstance(depth, MarketDepth)


@pytest.mark.asyncio
async def test_get_market_depth_batch(client):
    """Test batch fetching market depth for multiple symbols"""
    symbols = ["ACI", "GP", "BRACBANK"]
    result = await client.market.get_market_depth_batch(symbols)

    assert isinstance(result, dict)
    assert len(result) == len(symbols)
    for symbol in symbols:
        assert symbol in result


@pytest.mark.asyncio
async def test_get_sector_listed(client):
    """Test fetching list of sectors"""
    df = await client.market.get_sector_listed()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    cols_lower = [str(c).lower() for c in df.columns]
    assert any("sector" in c for c in cols_lower)


@pytest.mark.asyncio
async def test_get_latest_share_price_by_sector_by_name(client):
    """Test fetching latest share price by sector name"""
    df = await client.market.get_latest_share_price_by_sector("Bank")

    assert isinstance(df, pd.DataFrame)
    # May be empty or have data


@pytest.mark.asyncio
async def test_get_latest_share_price_by_sector_by_code(client):
    """Test fetching latest share price by sector code"""
    # First get a sector code
    sectors = await client.market.get_sector_listed()
    if not sectors.empty and "Code" in sectors.columns:
        sector_code = str(sectors.iloc[0]["Code"])
        df = await client.market.get_latest_share_price_by_sector(sector_code)
        assert isinstance(df, pd.DataFrame)


@pytest.mark.asyncio
async def test_get_top_stocks(client):
    """Test fetching top performing stocks"""
    df = await client.market.get_top_stocks()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Should have symbol/code column
    cols_lower = [str(c).lower() for c in df.columns]
    assert any("symbol" in c or "code" in c for c in cols_lower)


@pytest.mark.asyncio
async def test_get_top_10_gainers(client):
    """Test fetching top 10 gainers"""
    df = await client.market.get_top_10_gainers()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Should have symbol and change columns
    cols_lower = [str(c).lower() for c in df.columns]
    assert any("symbol" in c or "code" in c for c in cols_lower)
    assert any("change" in c for c in cols_lower)


@pytest.mark.asyncio
async def test_get_top_10_losers(client):
    """Test fetching top 10 losers"""
    try:
        df = await client.market.get_top_10_losers()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # Should have symbol and change columns
        cols_lower = [str(c).lower() for c in df.columns]
        assert any("symbol" in c or "code" in c for c in cols_lower)
        assert any("change" in c for c in cols_lower)
    except Exception as e:
        # This endpoint may not be available on DSE
        if "404" in str(e) or "HTTPStatusError" in str(type(e).__name__):
            pytest.skip("Top 10 losers endpoint not available on DSE")
        raise


@pytest.mark.asyncio
async def test_company_info_structure(client, sample_symbol):
    """Test company info returns proper structure"""
    data = await client.market.get_company_info(sample_symbol)

    # Check all major sections exist
    assert hasattr(data, "basic_information")
    assert hasattr(data, "market_information")
    assert hasattr(data, "financial_performance")
    assert hasattr(data, "interim_financial_performance")
    assert hasattr(data, "pe_ratios")
    assert hasattr(data, "other_information")
    assert hasattr(data, "corporate_performance")
    assert hasattr(data, "address")

    # Check basic information fields
    if data.basic_information.company_name:
        assert isinstance(data.basic_information.company_name, str)
    if data.basic_information.trading_code:
        assert isinstance(data.basic_information.trading_code, str)


@pytest.mark.asyncio
async def test_market_depth_structure(client, sample_symbol):
    """Test market depth returns proper structure"""
    depth = await client.market.get_market_depth(sample_symbol)

    if depth is not None:
        assert isinstance(depth, MarketDepth)
        # Check expected fields exist
        assert hasattr(depth, "buy_price")
        assert hasattr(depth, "buy_volume")
        assert hasattr(depth, "sell_price")
        assert hasattr(depth, "sell_volume")

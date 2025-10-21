"""Tests for news repository"""

import pytest
import httpx

from bdfinance.models.news import AGMNews, News


@pytest.mark.asyncio
async def test_get_agm_news(client):
    """Test fetching AGM news"""
    data = await client.news.get_agm_news()

    assert isinstance(data, list)
    # May be empty if no AGM scheduled
    if len(data) > 0:
        assert all(isinstance(item, AGMNews) for item in data)
        # Check first item has expected fields
        first = data[0]
        assert hasattr(first, "company")


@pytest.mark.asyncio
async def test_get_all_news(client):
    """Test fetching all news"""
    try:
        data = await client.news.get_all_news()
        assert isinstance(data, list)
        # May be empty
        if len(data) > 0:
            assert all(isinstance(item, News) for item in data)
            # Check first item has expected fields
            first = data[0]
            assert hasattr(first, "news_title") or hasattr(first, "news")
    except httpx.TooManyRedirects:
        # News endpoint may be having issues
        pytest.skip("News endpoint is experiencing redirect issues")


@pytest.mark.asyncio
async def test_get_all_news_empty_symbol(client):
    """Test fetching all news with None symbol"""
    try:
        data = await client.news.get_all_news(None)
        assert isinstance(data, list)
    except httpx.TooManyRedirects:
        pytest.skip("News endpoint is experiencing redirect issues")


@pytest.mark.asyncio
async def test_get_news_for_symbol(client, sample_symbol):
    """Test fetching news for specific symbol"""
    try:
        data = await client.news.get_all_news(sample_symbol)
        assert isinstance(data, list)
        # News may or may not be available for the symbol
    except httpx.TooManyRedirects:
        pytest.skip("News endpoint is experiencing redirect issues")


@pytest.mark.asyncio
async def test_get_news_for_multiple_symbols(client, sample_symbols):
    """Test fetching news for multiple symbols"""
    try:
        for symbol in sample_symbols[:3]:  # Test first 3 symbols
            data = await client.news.get_all_news(symbol)
            assert isinstance(data, list)
    except httpx.TooManyRedirects:
        pytest.skip("News endpoint is experiencing redirect issues")


@pytest.mark.asyncio
async def test_agm_news_structure(client):
    """Test AGM news structure"""
    data = await client.news.get_agm_news()

    if len(data) > 0:
        first = data[0]
        assert isinstance(first, AGMNews)
        # Check expected fields based on AGMNews model
        assert hasattr(first, "company")


@pytest.mark.asyncio
async def test_news_structure(client):
    """Test news structure"""
    try:
        data = await client.news.get_all_news()

        if len(data) > 0:
            first = data[0]
            assert isinstance(first, News)
            # Check expected fields based on News model
            assert hasattr(first, "news_title") or hasattr(first, "news")
    except httpx.TooManyRedirects:
        pytest.skip("News endpoint is experiencing redirect issues")


@pytest.mark.asyncio
async def test_news_caching(client, sample_symbol):
    """Test that news data is cached"""
    import time

    try:
        # First call (cache miss)
        start = time.time()
        data1 = await client.news.get_all_news(sample_symbol)
        time1 = time.time() - start

        # Second call (cache hit)
        start = time.time()
        data2 = await client.news.get_all_news(sample_symbol)
        time2 = time.time() - start

        # Cache hit should be faster
        assert time2 < time1 * 0.5  # At least 50% faster
        assert data1 == data2
    except httpx.TooManyRedirects:
        pytest.skip("News endpoint is experiencing redirect issues")

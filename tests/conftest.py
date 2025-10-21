"""Pytest configuration and fixtures"""

from pathlib import Path
import sys

import pytest
import pytest_asyncio

# One level up to import bdfinance
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bdfinance import BDStockClient


@pytest_asyncio.fixture
async def client():
    """Create a BDStockClient for testing"""
    async with BDStockClient() as client:
        yield client


@pytest.fixture
def sample_symbols():
    """Sample symbols for testing"""
    return ["ACI", "GP", "BRACBANK", "SQURPHARMA", "BATBC"]


@pytest.fixture
def sample_symbol():
    """Single sample symbol for testing"""
    return "ACI"
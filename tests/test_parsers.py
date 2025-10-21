"""Tests for HTML parsers"""

import pytest
from bdfinance.parsers import HTMLParser


@pytest.fixture
def sample_current_trade_html():
    """Sample HTML for current trade data"""
    return """
    <table class="table table-bordered background-white shares-table fixedHeader">
        <tr>
            <th>#</th>
            <th>Symbol</th>
            <th>LTP</th>
            <th>High</th>
            <th>Low</th>
            <th>Close</th>
            <th>YCP</th>
            <th>Change</th>
            <th>Trade</th>
            <th>Value</th>
            <th>Volume</th>
        </tr>
        <tr>
            <td>1</td>
            <td>ACI</td>
            <td>168.90</td>
            <td>174.00</td>
            <td>165.50</td>
            <td>168.90</td>
            <td>165.80</td>
            <td>3.10</td>
            <td>217</td>
            <td>2.36</td>
            <td>13,923</td>
        </tr>
        <tr>
            <td>2</td>
            <td>GP</td>
            <td>50.20</td>
            <td>51.00</td>
            <td>49.80</td>
            <td>50.20</td>
            <td>50.00</td>
            <td>0.20</td>
            <td>150</td>
            <td>1.50</td>
            <td>10,000</td>
        </tr>
    </table>
    """


@pytest.fixture
def sample_historical_data_html():
    """Sample HTML for historical data"""
    return """
    <table class="table table-bordered background-white shares-table fixedHeader">
        <tr>
            <th>#</th>
            <th>Date</th>
            <th>Symbol</th>
            <th>LTP</th>
            <th>High</th>
            <th>Low</th>
            <th>Open</th>
            <th>Close</th>
            <th>YCP</th>
            <th>Trade</th>
            <th>Value</th>
            <th>Volume</th>
        </tr>
        <tr>
            <td>1</td>
            <td>2025-10-15</td>
            <td>ACI</td>
            <td>168.90</td>
            <td>174.00</td>
            <td>165.50</td>
            <td>165.50</td>
            <td>168.90</td>
            <td>165.80</td>
            <td>217</td>
            <td>2.36</td>
            <td>13,923</td>
        </tr>
    </table>
    """


@pytest.fixture
def sample_agm_news_html():
    """Sample HTML for AGM news"""
    return """
    <table>
        <tr><th>Header 1</th></tr>
        <tr><th>Header 2</th></tr>
        <tr><th>Header 3</th></tr>
        <tr><th>Header 4</th></tr>
        <tr>
            <td>Advanced Chemical Industries PLC</td>
            <td>2024</td>
            <td>20%, 15%B</td>
            <td>29-Dec-2024</td>
            <td>01-Dec-2024</td>
            <td>Hotel Radisson Blu Dhaka</td>
            <td>10:00 AM</td>
        </tr>
        <tr>
            <td>Grameenphone Ltd.</td>
            <td>2024</td>
            <td>100%</td>
            <td>15-Nov-2024</td>
            <td>01-Nov-2024</td>
            <td>Sonargaon Hotel</td>
            <td>11:00 AM</td>
        </tr>
        <tr><td>Footer 1</td></tr>
        <tr><td>Footer 2</td></tr>
        <tr><td>Footer 3</td></tr>
        <tr><td>Footer 4</td></tr>
        <tr><td>Footer 5</td></tr>
        <tr><td>Footer 6</td></tr>
    </table>
    """


@pytest.fixture
def sample_news_html():
    """Sample HTML for general news"""
    return """
    <table class="table-news">
        <tr>
            <th>News Title:</th>
            <td>ACI Limited declares dividend</td>
        </tr>
        <tr>
            <th>News:</th>
            <td>The board has declared 20% cash dividend and 15% bonus shares.</td>
        </tr>
        <tr>
            <th>Post Date:</th>
            <td>2024-10-15</td>
        </tr>
        <tr>
            <th>News Title:</th>
            <td>GP announces quarterly results</td>
        </tr>
        <tr>
            <th>News:</th>
            <td>Grameenphone announces strong Q3 results.</td>
        </tr>
        <tr>
            <th>Post Date:</th>
            <td>2024-10-14</td>
        </tr>
    </table>
    """


@pytest.fixture
def sample_market_depth_html():
    """Sample HTML for market depth"""
    return """
    <table class="table table-stripped">
        <tr>
            <td valign="top">
                <table>
                    <tr><th>Buy Price</th><th>Buy Volume</th></tr>
                    <tr><th>Header</th><th>Header</th></tr>
                    <tr>
                        <td>168.50</td>
                        <td>1,000</td>
                    </tr>
                    <tr>
                        <td>168.00</td>
                        <td>2,500</td>
                    </tr>
                </table>
            </td>
            <td valign="top">
                <table>
                    <tr><th>Sell Price</th><th>Sell Volume</th></tr>
                    <tr><th>Header</th><th>Header</th></tr>
                    <tr>
                        <td>169.00</td>
                        <td>1,500</td>
                    </tr>
                    <tr>
                        <td>169.50</td>
                        <td>3,000</td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    """


@pytest.fixture
def sample_index_data_html():
    """Sample HTML for index data"""
    return """
    <div id="RightBody">
        <table>
            <tr>
                <th colspan="4">Market Summary of Oct 14, 2025</th>
            </tr>
            <tr>
                <td>DSEX Index</td>
                <td>5,234.56</td>
                <td>DSEX Index Change</td>
                <td>12.34</td>
            </tr>
            <tr>
                <td>DS30 Index</td>
                <td>1,890.12</td>
                <td>DS30 Index Change</td>
                <td>5.67</td>
            </tr>
            <tr>
                <td>Total Trade</td>
                <td>45,678</td>
                <td>Total Volume</td>
                <td>123,456,789</td>
            </tr>
            <tr>
                <td>Total Value Taka(mn)</td>
                <td>8,901.23</td>
                <td>Total Market Cap. Taka(mn)</td>
                <td>6,789,012.34</td>
            </tr>
        </table>
    </div>
    """


def test_parse_current_trade_data(sample_current_trade_html):
    """Test parsing current trade data"""
    result = HTMLParser.parse_current_trade_data(sample_current_trade_html)

    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check first row
    first = result[0]
    assert first["Symbol"] == "ACI"
    assert first["LTP"] == 168.90
    assert first["High"] == 174.00
    assert first["Low"] == 165.50
    assert first["Close"] == 168.90
    assert first["YCP"] == 165.80
    assert first["Change"] == 3.10
    assert first["Trade"] == 217
    assert first["Value"] == 2.36
    assert first["Volume"] == 13923

    # Check second row
    second = result[1]
    assert second["Symbol"] == "GP"
    assert second["LTP"] == 50.20
    assert second["Volume"] == 10000


def test_parse_historical_data(sample_historical_data_html):
    """Test parsing historical data"""
    result = HTMLParser.parse_historical_data(sample_historical_data_html)

    assert isinstance(result, list)
    assert len(result) == 1
    
    first = result[0]
    # Date is returned as datetime object or string
    assert "Date" in first
    assert first["Symbol"] == "ACI"
    assert first["LTP"] == 168.90
    assert first["High"] == 174.00
    assert first["Low"] == 165.50
    assert first["Open"] == 165.50
    assert first["Close"] == 168.90
    assert first["YCP"] == 165.80
    assert first["Trade"] == 217
    assert first["Value"] == 2.36
    assert first["Volume"] == 13923


def test_parse_agm_news(sample_agm_news_html):
    """Test parsing AGM news"""
    result = HTMLParser.parse_agm_news(sample_agm_news_html)

    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check first news
    first = result[0]
    assert first["Company"] == "Advanced Chemical Industries PLC"
    assert first["Year End"] == "2024"
    assert first["Dividend"] == "20%, 15%B"
    assert first["Date of AGM/EGM"] == "29-Dec-2024"
    assert first["Record Date"] == "01-Dec-2024"
    assert first["Venue"] == "Hotel Radisson Blu Dhaka"
    assert first["Time"] == "10:00 AM"

    # Check second news
    second = result[1]
    assert second["Company"] == "Grameenphone Ltd."
    assert second["Dividend"] == "100%"


def test_parse_news(sample_news_html):
    """Test parsing general news"""
    result = HTMLParser.parse_news(sample_news_html)

    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check first news
    first = result[0]
    assert first["News Title"] == "ACI Limited declares dividend"
    assert "20% cash dividend" in first["News"]
    assert first["Post Date"] == "2024-10-15"

    # Check second news
    second = result[1]
    assert second["News Title"] == "GP announces quarterly results"
    assert "Q3 results" in second["News"]


def test_parse_market_depth(sample_market_depth_html):
    """Test parsing market depth"""
    result = HTMLParser.parse_market_depth(sample_market_depth_html)

    assert isinstance(result, list)
    assert len(result) >= 2
    
    # Check structure - should have buy and sell data
    for item in result:
        assert isinstance(item, dict)
        # Each item should have either buy or sell data
        has_buy = "buy_price" in item and "buy_volume" in item
        has_sell = "sell_price" in item and "sell_volume" in item
        assert has_buy or has_sell


def test_parse_index_data(sample_index_data_html):
    """Test parsing index data"""
    result = HTMLParser.parse_index_data(sample_index_data_html)

    assert isinstance(result, list)
    assert len(result) >= 1
    
    first = result[0]
    # Date is returned as datetime object or string
    assert "Date" in first
    assert first["Symbol"] == "DSEX"
    assert "DSEX" in first
    assert "DSEX Change" in first
    assert "DS30" in first
    assert "DS30 Change" in first
    assert "Trade" in first
    assert "Volume" in first
    assert "Value" in first
    assert "Market Cap" in first


def test_parse_current_trade_data_empty():
    """Test parsing with empty/invalid HTML"""
    result = HTMLParser.parse_current_trade_data("<html></html>")
    assert result == []


def test_parse_historical_data_empty():
    """Test parsing historical data with empty HTML"""
    result = HTMLParser.parse_historical_data("<html></html>")
    assert result == []


def test_parse_agm_news_empty():
    """Test parsing AGM news with empty HTML"""
    result = HTMLParser.parse_agm_news("<html></html>")
    assert result == []


def test_parse_news_empty():
    """Test parsing news with empty HTML"""
    result = HTMLParser.parse_news("<html></html>")
    assert result == []


def test_parse_market_depth_empty():
    """Test parsing market depth with empty HTML"""
    result = HTMLParser.parse_market_depth("<html></html>")
    assert result == []


def test_parse_index_data_empty():
    """Test parsing index data with empty HTML"""
    result = HTMLParser.parse_index_data("<html></html>")
    assert result == []


def test_parse_simple_table():
    """Test parsing simple table"""
    html = """
    <table>
        <tr>
            <th>Symbol</th>
            <th>Price</th>
            <th>Change</th>
        </tr>
        <tr>
            <td>ACI</td>
            <td>168.90</td>
            <td>3.10</td>
        </tr>
        <tr>
            <td>GP</td>
            <td>50.20</td>
            <td>0.20</td>
        </tr>
    </table>
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    
    assert table is not None
    result = HTMLParser.parse_simple_table(table)
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["Symbol"] == "ACI"
    assert result[0]["Price"] == "168.90"
    assert result[1]["Symbol"] == "GP"


def test_parse_simple_table_with_mappings():
    """Test parsing simple table with column mappings"""
    html = """
    <table>
        <tr>
            <th>Trade Code</th>
            <th>LTP</th>
        </tr>
        <tr>
            <td>ACI</td>
            <td>168.90</td>
        </tr>
    </table>
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    
    assert table is not None
    result = HTMLParser.parse_simple_table(
        table,
        mappings={"Trade Code": "Symbol", "LTP": "Price"}
    )
    
    assert result is not None
    assert result[0]["Symbol"] == "ACI"
    assert result[0]["Price"] == "168.90"
    assert "Trade Code" not in result[0]


def test_parse_simple_table_with_transform():
    """Test parsing simple table with value transformation"""
    html = """
    <table>
        <tr>
            <th>Symbol</th>
            <th>Price</th>
        </tr>
        <tr>
            <td>aci</td>
            <td>168.90</td>
        </tr>
    </table>
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    
    assert table is not None
    result = HTMLParser.parse_simple_table(
        table,
        transform_values={"Symbol": lambda x: x.upper()}
    )
    
    assert result is not None
    assert result[0]["Symbol"] == "ACI"
    assert result[0]["Price"] == "168.90"

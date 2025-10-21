"""Constants for DSE URLs and endpoints"""

from typing import Final

# Base URLs
DSE_URL: Final[str] = "https://dsebd.org/"
DSE_ALT_URL: Final[str] = "https://dsebd.com.bd/"

# Trading endpoints
DSE_DEA_URL: Final[str] = "day_end_archive.php"
DSE_LSP_URL: Final[str] = "latest_share_price_scroll_l.php"
DSE_CLOSE_PRICE_URL: Final[str] = "dse_close_price_archive.php"
DSEX_INDEX_VALUE: Final[str] = "dseX_share.php"
DSE_LTP_URL: Final[str] = "ltp_industry.php"

# Market endpoints
DSE_COMPANY_INFO_URL: Final[str] = "displayCompany.php"
DSE_MARKET_INFO_URL: Final[str] = "recent_market_information.php"
DSE_MARKET_INFO_MORE_URL: Final[str] = "recent_market_information_more.php"
DSE_MARKET_DEPTH_URL: Final[str] = "ajax/load-instrument.php"
DSE_MARKET_DEPTH_REFERER_URL: Final[str] = "mkt_depth_3.php"
DSE_LPE_URL: Final[str] = "latest_PE.php"
DSE_COMPANY_LIST_URL: Final[str] = "company_listing.php"
DSE_MARKET_SUMMARY_URL: Final[str] = "market_summary.php"
DSE_SECTOR_LIST_URL: Final[str] = "by_industrylisting.php"
DSE_TOP_STOCKS_URL: Final[str] = "top_20_share.php"
DSE_TOP_10_GAINERS_URL: Final[str] = "top_ten_gainer.php"
DSE_TOP_10_LOSERS_URL: Final[str] = "top_ten_loser.php"

# News endpoints
DSE_AGM_URL: Final[str] = "Company_AGM.htm"
DSE_NEWS_URL: Final[str] = "old_news.php"

WIKIPEDIA_API_URL: Final[str] = "https://en.wikipedia.org/w/api.php"

# User agent
USER_AGENT: Final[str] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

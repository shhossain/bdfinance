"""News repository with async methods"""

import structlog

from bdfinance import constants
from bdfinance.models.news import AGMNews, News
from bdfinance.repositories.base import BaseRepository, RequestPayload

logger = structlog.get_logger()


class NewsRepository(BaseRepository):
    """Repository for news data operations"""

    async def get_agm_news(self) -> list[AGMNews]:
        """Get AGM (Annual General Meeting) news"""
        # Fetch data using get_data
        payload: RequestPayload = {
            "url": constants.DSE_AGM_URL,
            "key": "agm_news",
            "parser": "parse_agm_news",
            "method": "GET",
            "ttl": 3600,
        }
        news_data = await self.get_data(payload)

        if not news_data:
            return []

        # Parse with Pydantic - map capitalized keys to lowercase
        agm_news = []
        for data in news_data:
            mapped_data = {
                "company": data.get("Company", ""),
                "year_end": data.get("Year End", ""),
                "dividend": data.get("Dividend", ""),
                "agm_date": data.get("Date of AGM/EGM", ""),
                "record_date": data.get("Record Date", ""),
                "venue": data.get("Venue", ""),
                "time": data.get("Time", ""),
            }
            agm_news.append(AGMNews(**mapped_data))

        return agm_news

    async def get_all_news(self, symbol: str | None = None) -> list[News]:
        """Get all news or news for specific code"""
        # Fetch data using get_data
        payload: RequestPayload = {
            "url": constants.DSE_NEWS_URL,
            "key": f"all_news_{symbol or 'all'}",
            "parser": "parse_news",
            "data": {
                "inst": symbol,
                "criteria": 3,
                "archive": "news",
            },
            "method": "POST",
            "ttl": 1800,
        }
        news_data = await self.get_data(payload)

        if not news_data:
            return []

        # Parse with Pydantic - map capitalized keys to lowercase
        news_list = []
        for data in news_data:
            mapped_data = {
                "news_title": data.get("News Title"),
                "news": data.get("News"),
                "post_date": data.get("Post Date"),
            }
            news_list.append(News(**mapped_data))

        return news_list

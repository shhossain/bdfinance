"""Pydantic models for news data"""


from pydantic import BaseModel, Field


class AGMNews(BaseModel):
    """AGM (Annual General Meeting) news"""

    company: str = Field(description="Company name")
    year_end: str = Field(description="Year end date")
    dividend: str = Field(description="Dividend information")
    agm_date: str = Field(description="AGM date")
    record_date: str = Field(description="Record date")
    venue: str = Field(description="Venue")
    time: str = Field(description="Time")


class News(BaseModel):
    """General news item"""

    news_title: str | None = Field(None, description="News title")
    news: str | None = Field(None, description="News content")
    post_date: str | None = Field(None, description="Post date")

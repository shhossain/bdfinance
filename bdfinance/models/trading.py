"""Pydantic models for trading data"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CurrentTradeData(BaseModel):
    """Current trading data for a stock"""

    symbol: str = Field(description="Stock symbol")
    ltp: float = Field(description="Last traded price")
    high: float = Field(description="Day high")
    low: float = Field(description="Day low")
    close: float = Field(description="Close price")
    ycp: float = Field(description="Yesterday's closing price")
    change: float = Field(description="Price change")
    trade: int = Field(description="Number of trades")
    value: float = Field(description="Total value traded")
    volume: int = Field(description="Total volume traded")

    @field_validator("symbol", mode="before")
    @classmethod
    def clean_symbol(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator(
        "ltp", "high", "low", "close", "ycp", "change", "value", mode="before"
    )
    @classmethod
    def clean_float(cls, v: str | float) -> float:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0.0
            return float(v) if v else 0.0
        return float(v)

    @field_validator("trade", "volume", mode="before")
    @classmethod
    def clean_int(cls, v: str | int) -> int:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0
            return int(v) if v else 0
        return int(v)



class BasicHistoricalData(BaseModel):
    """Simplified historical data (OHLCV)"""

    date: datetime = Field(description="Trading date")
    open: float = Field(description="Opening price")
    high: float = Field(description="Day high")
    low: float = Field(description="Day low")
    close: float = Field(description="Closing price")
    volume: int = Field(description="Total volume traded")

    @field_validator("open", "high", "low", "close", mode="before")
    @classmethod
    def clean_float(cls, v: str | float) -> float:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0.0
            return float(v) if v else 0.0
        return float(v)

    @field_validator("volume", mode="before")
    @classmethod
    def clean_int(cls, v: str | int) -> int:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0
            return int(v) if v else 0
        return int(v)


class ClosePriceData(BaseModel):
    """Close price data"""

    date: datetime = Field(description="Trading date")
    symbol: str = Field(description="Stock symbol")
    close: float = Field(description="Closing price")
    ycp: float = Field(description="Yesterday's closing price")

    @field_validator("symbol", mode="before")
    @classmethod
    def clean_symbol(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("close", "ycp", mode="before")
    @classmethod
    def clean_float(cls, v: str | float) -> float:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0.0
            return float(v) if v else 0.0
        return float(v)


class TradingSymbol(BaseModel):
    """Trading code/symbol"""

    symbol: str = Field(description="Stock symbol")

    @field_validator("symbol", mode="before")
    @classmethod
    def clean_symbol(cls, v: str) -> str:
        return v.strip().upper()

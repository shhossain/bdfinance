"""Pydantic models for market data"""

from pydantic import BaseModel, Field, field_validator


class MarketInfo(BaseModel):
    """Market information data"""

    date: str = Field(description="Date")
    total_trade: int = Field(description="Total number of trades")
    total_volume: int = Field(description="Total volume")
    total_value: float = Field(description="Total value in millions")
    total_market_cap: float = Field(description="Total market cap in millions")
    dsex_index: float = Field(description="DSEX index value")
    dses_index: float = Field(description="DSES index value")
    ds30_index: float = Field(description="DS30 index value")
    dgen_index: float = Field(description="DGEN index value")

    @field_validator("total_trade", "total_volume", mode="before")
    @classmethod
    def clean_int(cls, v: str | int) -> int:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0
            return int(v) if v else 0
        return int(v)

    @field_validator(
        "total_value",
        "total_market_cap",
        "dsex_index",
        "dses_index",
        "ds30_index",
        "dgen_index",
        mode="before",
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



class MarketDepth(BaseModel):
    """Market depth data (bid/ask)"""

    buy_price: float = Field(default=0.0, description="Buy price")
    buy_volume: int = Field(default=0, description="Buy volume")
    sell_price: float = Field(default=0.0, description="Sell price")
    sell_volume: int = Field(default=0, description="Sell volume")

    @field_validator("buy_price", "sell_price", mode="before")
    @classmethod
    def clean_float(cls, v: str | float) -> float:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0.0
            return float(v) if v else 0.0
        return float(v)

    @field_validator("buy_volume", "sell_volume", mode="before")
    @classmethod
    def clean_int(cls, v: str | int) -> int:
        if isinstance(v, str):
            v = v.replace(",", "").replace("n/a", "0").replace("N/A", "0").strip()
            # Handle standalone dash or empty after cleanup
            if v in ("-", "", "--"):
                return 0
            return int(v) if v else 0
        return int(v)


class CompanyInfo(BaseModel):
    data: dict = Field(description="Company information data")

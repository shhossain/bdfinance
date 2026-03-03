"""Pydantic models for DSE company information"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

class DividendRecord(BaseModel):
    """Dividend record (cash or bonus)"""

    percentage: float
    label: str | None = None
    year: int



class RightIssueRecord(BaseModel):
    """Right issue record"""

    ratio: str
    price: str | None = None
    year: int


class ShortInfo(BaseModel):
    """Short company information"""

    company_name: str
    trading_code: str
    scrip_code: str


class MarketInformation(BaseModel):
    """Market information - all fields are consistently present"""

    last_trading_price: float | None = None
    closing_price: float | None = None
    last_updated: datetime | None = None
    opening_price: float | None = None
    adjusted_opening_price: float | None = None
    yesterday_closing_price: float | None = None
    days_range: str | None = None
    days_value_mn: float | None = None
    weeks_52_range: str | None = None
    days_volume: float | None = None
    days_trade: int | None = None
    market_cap_mn: float | None = None
    change_value: float | None = None
    change_percentage: float | None = None


class BasicInformation(BaseModel):
    """Basic company information - core fields always present"""

    # Always present fields based on API testing
    company_name: str
    trading_code: str
    scrip_code: str

    # Financial metrics - usually present
    authorized_capital_mn: float | None = None
    paid_up_capital_mn: float | None = None
    face_value: float | None = None
    total_outstanding_securities: float | None = None
    market_lot: float | None = None
    reserve_surplus_mn: float | None = None
    oci_mn: float | None = None

    # Dates
    debut_trading_date: datetime | None = None
    last_agm_date: datetime | None = None
    financial_year_ended: datetime | None = None

    # Categorical
    instrument_type: str | None = None
    sector: str | None = None
    year_end: str | None = None

    # Dividend and corporate actions
    cash_dividends: list[DividendRecord] = Field(default_factory=list)
    bonus_issues: list[DividendRecord] = Field(default_factory=list)
    right_issue: list[RightIssueRecord] = Field(default_factory=list)

    # Optional summary
    summary: str | None = None

class InterimEPS(BaseModel):
    """Interim EPS data for a period"""

    eps_basic: float | None = None
    eps_diluted: float | None = None
    eps_continuing_basic: float | None = None
    eps_continuing_diluted: float | None = None
    market_price: float | None = None



class InterimFinancialPerformance(BaseModel):
    """Interim financial performance by quarter"""

    year: int | None = None
    q1: InterimEPS = Field(default_factory=InterimEPS)
    q2: InterimEPS = Field(default_factory=InterimEPS)
    half_yearly: InterimEPS = Field(default_factory=InterimEPS)
    q3: InterimEPS = Field(default_factory=InterimEPS)
    nine_months: InterimEPS = Field(default_factory=InterimEPS)
    annual: InterimEPS = Field(default_factory=InterimEPS)

        

class PERatioEntry(BaseModel):
    """P/E ratio entry"""

    date: datetime
    metric: str
    value: float


class PERatios(BaseModel):
    """P/E ratios from unaudited and audited statements"""

    unaudited: list[PERatioEntry] = Field(default_factory=list)
    audited: list[PERatioEntry] = Field(default_factory=list)



class FinancialPerformanceAudited(BaseModel):
    """Audited financial performance statement"""

    # Required
    year: int

    # EPS metrics
    eps_basic_original: float | None = None
    eps_basic_restated: float | None = None
    eps_diluted: float | None = None
    eps_continuing_basic_original: float | None = None
    eps_continuing_basic_restated: float | None = None
    eps_continuing_diluted: float | None = None

    # NAV metrics
    nav_per_share_original: float | None = None
    nav_per_share_restated: float | None = None
    nav_per_share_diluted: float | None = None

    # Profit metrics
    profit_continuing_mn: float | None = None
    profit_for_year_mn: float | None = None
    total_comprehensive_income_mn: float | None = None

    # PE ratios
    pe_ratio_basic_original: float | None = None
    pe_ratio_basic_restated: float | None = None
    pe_ratio_diluted: float | None = None
    pe_continuing_basic_original: float | None = None
    pe_continuing_basic_restated: float | None = None
    pe_continuing_diluted: float | None = None

    # Dividend information
    dividend_percent: float | None = None
    dividend_type: Literal["Cash", "Bonus"] | None = None
    dividend_yield_percent: float | None = None

        


class FinancialPerformance(BaseModel):
    """Financial performance section with audited statements"""

    statements: list[FinancialPerformanceAudited] = Field(default_factory=list)
    financial_statement_url: str | None = None
    price_sensitive_info_url: str | None = None
    audited_by: str
        

class ShareholdingEntry(BaseModel):
    """Shareholding entry"""

    date: datetime | None = None
    sponsor_director: float | None = None
    govt: float | None = None
    institute: float | None = None
    foreign: float | None = None
    public: float | None = None


class OtherInformation(BaseModel):
    """Other company information"""

    listing_year: int | None = None
    market_category: str | None = None
    electronic_share: str | None = None
    remarks: str | None = None
    shareholding: list[ShareholdingEntry] = Field(default_factory=list)


class CorporatePerformance(BaseModel):
    """Corporate performance metrics"""

    operational_status: str | None = None
    short_term_loan_mn: float | None = None
    long_term_loan_mn: float | None = None
    latest_dividend: str | None = None
    credit_rating_short_term: str | None = None
    credit_rating_long_term: str | None = None
    otc_delisting_relisting: str | None = None


class CompanyAddress(BaseModel):
    """Company address and contact information"""

    # Core fields - usually present
    head_office: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    company_secretary: str | None = None

    # Optional contact fields
    factory: str | None = None
    fax: str | None = None
    secretary_cell: str | None = None
    secretary_telephone: str | None = None
    secretary_email: str | None = None


class DSECompanyData(BaseModel):
    """Complete DSE company information"""

    # Core sections - always present based on API testing
    basic_information: BasicInformation
    market_information: MarketInformation
    financial_performance: FinancialPerformance
    interim_financial_performance: InterimFinancialPerformance
    pe_ratios: PERatios
    other_information: OtherInformation
    corporate_performance: CorporatePerformance
    address: CompanyAddress

    @field_validator("basic_information", mode="before")
    @classmethod
    def validate_basic_info(cls, v):
        """Ensure basic information has required fields"""
        if isinstance(v, dict):
            # Merge short info if present
            if "company_name" not in v and "trading_code" in v:
                raise ValueError("BasicInformation must have company_name")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "basic_information": {
                    "company_name": "Grameenphone Ltd.",
                    "trading_code": "GP",
                    "scrip_code": "19404",
                },
                "market_information": {
                    "last_trading_price": 323.0,
                    "closing_price": 323.0,
                },
            }
        }
    )
        
        

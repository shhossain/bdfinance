"""Tests for Pydantic company models"""
import pytest
from datetime import datetime
from bdfinance.models.company import (
    BasicInformation,
    CompanyAddress,
    CorporatePerformance,
    DividendRecord,
    DSECompanyData,
    FinancialPerformance,
    FinancialPerformanceAudited,
    InterimEPS,
    InterimFinancialPerformance,
    MarketInformation,
    OtherInformation,
    PERatios,
    RightIssueRecord,
)


class TestDividendRecord:
    """Test DividendRecord model"""

    def test_create_dividend_record(self):
        """Test creating a dividend record"""
        record = DividendRecord(
            percentage=10.0,
            label="Final",
            year=2024,
        )
        assert record.percentage == 10.0
        assert record.label == "Final"
        assert record.year == 2024

    def test_dividend_record_optional_label(self):
        """Test dividend record with optional label"""
        record = DividendRecord(
            percentage=15.5,
            label=None,
            year=2023,
        )
        assert record.label is None


class TestRightIssueRecord:
    """Test RightIssueRecord model"""

    def test_create_right_issue(self):
        """Test creating a right issue record"""
        record = RightIssueRecord(
            ratio="1:2",
            price="100.00",
            year=2024,
        )
        assert record.ratio == "1:2"
        assert record.price == "100.00"


class TestMarketInformation:
    """Test MarketInformation model"""

    def test_create_market_info(self):
        """Test creating market information"""
        info = MarketInformation(
            last_trading_price=323.0,
            closing_price=323.0,
            opening_price=320.0,
            days_volume=1000000.0,
        )
        assert info.last_trading_price == 323.0
        assert info.closing_price == 323.0

    def test_market_info_with_datetime(self):
        """Test market info with datetime"""
        now = datetime.now()
        info = MarketInformation(
            last_trading_price=323.0,
            last_updated=now,
        )
        assert info.last_updated == now


class TestBasicInformation:
    """Test BasicInformation model"""

    def test_create_basic_info(self):
        """Test creating basic information"""
        info = BasicInformation(
            company_name="Grameenphone Ltd.",
            trading_code="GP",
            scrip_code="19404",
            authorized_capital_mn=1000.0,
            paid_up_capital_mn=500.0,
        )
        assert info.company_name == "Grameenphone Ltd."
        assert info.trading_code == "GP"
        assert info.scrip_code == "19404"

    def test_basic_info_with_dividends(self):
        """Test basic info with dividend records"""
        info = BasicInformation(
            company_name="Test Company",
            trading_code="TEST",
            scrip_code="12345",
            cash_dividends=[
                DividendRecord(percentage=10.0, label="Final", year=2024)
            ],
            bonus_issues=[
                DividendRecord(percentage=20.0, label="Bonus", year=2023)
            ],
        )
        assert len(info.cash_dividends) == 1
        assert len(info.bonus_issues) == 1

    def test_basic_info_required_fields(self):
        """Test that required fields are enforced"""
        with pytest.raises(ValueError):
            # Missing company_name
            BasicInformation(
                trading_code="TEST",
                scrip_code="12345",
            )


class TestInterimFinancialPerformance:
    """Test InterimFinancialPerformance model"""

    def test_create_interim_performance(self):
        """Test creating interim performance"""
        perf = InterimFinancialPerformance(
            year=2024,
            q1=InterimEPS(eps_basic=10.5, eps_diluted=10.0),
            q2=InterimEPS(eps_basic=11.5, eps_diluted=11.0),
        )
        assert perf.year == 2024
        assert perf.q1.eps_basic == 10.5
        assert perf.q2.eps_diluted == 11.0


class TestFinancialPerformanceAudited:
    """Test FinancialPerformanceAudited model"""

    def test_create_audited_statement(self):
        """Test creating audited financial statement"""
        stmt = FinancialPerformanceAudited(
            year=2024,
            eps_continuing_basic_original=26.89,
            nav_per_share_original=47.95,
            profit_for_year_mn=36308.73,
            dividend_percent=330.0,
            dividend_type="Cash",
        )
        assert stmt.year == 2024
        assert stmt.eps_continuing_basic_original == 26.89
        assert stmt.dividend_type == "Cash"

    def test_dividend_type_validation(self):
        """Test dividend type accepts only Cash or Bonus"""
        # Should work with valid types
        stmt1 = FinancialPerformanceAudited(year=2024, dividend_type="Cash")
        stmt2 = FinancialPerformanceAudited(year=2024, dividend_type="Bonus")
        assert stmt1.dividend_type == "Cash"
        assert stmt2.dividend_type == "Bonus"


class TestCompanyAddress:
    """Test CompanyAddress model"""

    def test_create_address(self):
        """Test creating company address"""
        address = CompanyAddress(
            head_office="Dhaka, Bangladesh",
            phone="+880-1234567890",
            email="info@company.com",
            website="https://company.com",
            company_secretary="John Doe",
        )
        assert address.head_office == "Dhaka, Bangladesh"
        assert address.email == "info@company.com"

    def test_address_required_fields(self):
        """Test that required address fields are enforced"""
        with pytest.raises(ValueError):
            CompanyAddress(
                head_office="Dhaka",
                phone="+880-1234567890",
            )


class TestDSECompanyData:
    """Test DSECompanyData model"""

    def test_create_complete_company_data(self):
        """Test creating complete company data"""
        data = DSECompanyData(
            basic_information=BasicInformation(
                company_name="Test Company",
                trading_code="TEST",
                scrip_code="12345",
            ),
            market_information=MarketInformation(
                last_trading_price=100.0,
            ),
            financial_performance=FinancialPerformance(
                statements=[],
            ),
            interim_financial_performance=InterimFinancialPerformance(),
            pe_ratios=PERatios(),
            other_information=OtherInformation(shareholding=[]),
            corporate_performance=CorporatePerformance(),
            address=CompanyAddress(
                head_office="Test Office",
                phone="1234567890",
                email="test@test.com",
                website="https://test.com",
                company_secretary="Test Secretary",
            ),
        )
        assert data.basic_information.company_name == "Test Company"
        assert data.market_information.last_trading_price == 100.0

    def test_model_serialization(self):
        """Test that model can be serialized to dict"""
        data = DSECompanyData(
            basic_information=BasicInformation(
                company_name="Test",
                trading_code="TEST",
                scrip_code="123",
            ),
            market_information=MarketInformation(),
            financial_performance=FinancialPerformance(statements=[]),
            interim_financial_performance=InterimFinancialPerformance(),
            pe_ratios=PERatios(),
            other_information=OtherInformation(shareholding=[]),
            corporate_performance=CorporatePerformance(),
            address=CompanyAddress(
                head_office="Test",
                phone="123",
                email="test@test.com",
                website="https://test.com",
                company_secretary="Test",
            ),
        )
        data_dict = data.model_dump()
        assert isinstance(data_dict, dict)
        assert "basic_information" in data_dict
        assert data_dict["basic_information"]["company_name"] == "Test"

    def test_model_json_serialization(self):
        """Test that model can be serialized to JSON"""
        data = DSECompanyData(
            basic_information=BasicInformation(
                company_name="Test",
                trading_code="TEST",
                scrip_code="123",
            ),
            market_information=MarketInformation(),
            financial_performance=FinancialPerformance(statements=[]),
            interim_financial_performance=InterimFinancialPerformance(),
            pe_ratios=PERatios(),
            other_information=OtherInformation(shareholding=[]),
            corporate_performance=CorporatePerformance(),
            address=CompanyAddress(
                head_office="Test",
                phone="123",
                email="test@test.com",
                website="https://test.com",
                company_secretary="Test",
            ),
        )
        json_str = data.model_dump_json()
        assert isinstance(json_str, str)
        assert "Test" in json_str

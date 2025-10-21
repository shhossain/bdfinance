import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup, Tag
from dateutil.parser import parse as dateutil_parse

from bdfinance.models.company import (
    BasicInformation,
    CompanyAddress,
    CorporatePerformance,
    DividendRecord,
    DSECompanyData,
    FinancialPerformance,
    FinancialPerformanceAudited,
    InterimFinancialPerformance,
    MarketInformation,
    OtherInformation,
    PERatioEntry,
    PERatios,
    RightIssueRecord,
    ShareholdingEntry,
)
from bdfinance.utils.data_cleaners import clean_int


def parse_date(date_str: str) -> datetime | None:
    """Parse date strings in various formats."""
    if not date_str or date_str == "-":
        return None

    date_str = date_str.strip()
    # formats = [
    #     "%b %d, %Y",  # Oct 16, 2025
    #     "%d-%m-%Y",  # 21-04-2025
    #     "%d %b, %Y",  # 24 Dec, 2020
    #     "%B %d, %Y",  # October 16, 2025
    #     # Dec 31, 2024
    #     "%b %d, %Y",  # Dec 31, 2023
    # ]

    # for fmt in formats:
    #     try:
    #         return datetime.strptime(date_str, fmt)
    #     except ValueError:
    #         continue
    # return None
    try:
        return dateutil_parse(date_str)
    except (ValueError, OverflowError):
        return None


def parse_number(value: str) -> float | None:
    """Parse numeric values, handling commas and empty values."""
    if not value or value == "-" or value.strip() == "":
        return None

    # Remove commas and whitespace
    cleaned = value.replace(",", "").strip()

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_percentage(value: str) -> float | None:
    """Parse percentage values."""
    if not value or value == "-":
        return None

    cleaned = value.replace("%", "").strip()
    return parse_number(cleaned)


def parse_company_basic_info(table: Tag, h2: Tag) -> dict[str, str]:
    """Parse company name and trading codes."""
    info: dict[str, str] = {}

    text = h2.get_text()
    if "Company Name:" in text:
        # Extract company name from <i> tag
        i_tag = h2.find("i")
        if i_tag:
            info["company_name"] = i_tag.get_text(strip=True)

    for row in table.find_all("tr"):
        for th in row.find_all("th"):
            th_text = th.get_text(strip=True)

            if "Trading Code:" in th_text:
                parts = th_text.split("Trading Code:")
                if len(parts) > 1:
                    info["trading_code"] = parts[1].strip()

            if "Scrip Code:" in th_text:
                parts = th_text.split("Scrip Code:")
                if len(parts) > 1:
                    info["scrip_code"] = parts[1].strip()

    return info


def parse_market_information(table: Tag, h2: Tag) -> MarketInformation:
    """Parse market information section."""
    market_info: dict[str, Any] = {}

    rows = table.find_all("tr")
    parser_map = {
        "Last Trading Price": ("last_trading_price", parse_number),
        "Closing Price": ("closing_price", parse_number),
        "Last Update": ("last_update", lambda x: x if x and x != "-" else None),
        "Opening Price": ("opening_price", parse_number),
        "Adjusted Opening Price": ("adjusted_opening_price", parse_number),
        "Yesterday's Closing Price": ("yesterday_closing_price", parse_number),
        "Day's Range": ("days_range", lambda x: x if x and x != "-" else None),
        "Day's Value (mn)": ("days_value_mn", parse_number),
        "52 Weeks' Moving Range": (
            "weeks_52_range",
            lambda x: x if x and x != "-" else None,
        ),
        "Day's Volume": ("days_volume", parse_number),
        "Day's Trade": ("days_trade", clean_int),
        "Market Capitalization (mn)": ("market_cap_mn", parse_number),
        "Change": ("change_value", parse_number),
    }
    # sort parser_map by key length descending to match longer keys first
    parser_map = dict(sorted(parser_map.items(), key=lambda item: -len(item[0])))

    change_cell = None
    for row in rows:
        # Get all th and td elements
        ts = row.find_all(["th", "td"])
        if len(ts) == 3:
            change_cell = ts[0]
            ts = ts[1:]

        chunk_size = 2
        tts = [ts[i : i + chunk_size] for i in range(0, len(ts), chunk_size)]
        for pair in tts:
            if len(pair) != 2:
                continue
            key = pair[0].get_text(strip=True)
            value = pair[1].get_text(strip=True)

            for k, (field, func) in parser_map.items():
                if k in key:
                    market_info[field] = func(value)
                    break

    if change_cell:
        market_info["change_percentage"] = parse_percentage(
            change_cell.get_text(strip=True)
        )

    htext = h2.get_text(strip=True)
    date = htext.split(":")[-1].strip() if ":" in htext else ""
    if date:
        if "last_update" in market_info and market_info["last_update"]:
            # last update contains time
            time_part = market_info["last_update"]
            datetime_str = f"{date} {time_part}"
            market_info["last_updated"] = parse_date(datetime_str)
        else:
            market_info["last_updated"] = parse_date(date)
    else:
        market_info["last_updated"] = None

    market_info.pop("last_update", None)

    return MarketInformation(**market_info)


def parse_basic_information(table: Tag) -> dict[str, Any]:
    """Parse basic information section."""
    basic_info: dict[str, Any] = {}

    for row in table.find_all("tr", recursive=False):
        cells = row.find_all(["th", "td"])

        # Process each th-td pair
        i = 0
        while i < len(cells) - 1:
            if cells[i].name == "th":
                key = cells[i].get_text(strip=True)
                value = (
                    cells[i + 1].get_text(strip=True) if i + 1 < len(cells) else None
                )
                parse_map = {
                    "Authorized Capital": "authorized_capital_mn",
                    "Paid-up Capital": "paid_up_capital_mn",
                    "Face/par Value": "face_value",
                    "Total No. of Outstanding Securities": "total_outstanding_securities",
                    "Debut Trading Date": "debut_trading_date",
                    "Type of Instrument": "instrument_type",
                    "Market Lot": "market_lot",
                    "Sector": "sector",
                }

                for k, v in parse_map.items():
                    if k in key:
                        if v == "debut_trading_date":
                            basic_info[v] = parse_date(value) if value else None
                        elif v == "instrument_type" or v == "sector":
                            basic_info[v] = value if value and value != "-" else None
                        elif v == "total_outstanding_securities":
                            basic_info[v] = clean_int(value) if value else None
                        else:
                            basic_info[v] = parse_number(value) if value else None
                        break

                i += 2
            else:
                i += 1

    # Parse AGM and year-end information
    h2 = table.find_next("h2")
    divs = h2.find_all("div") if h2 else []
    if len(divs) >= 2:
        agm = divs[0]
        agm_text = agm.find("i")
        if agm_text:
            basic_info["last_agm_date"] = parse_date(agm_text.get_text(strip=True))
        year_text = divs[1].get_text(strip=True)
        if year_text:
            basic_info["financial_year_ended"] = parse_date(
                year_text.split(":")[-1].strip()
            )

    current = table.find_next("table")
    if current:
        current = current.find_next("table")
    for row in current.find_all("tr") if current else []:
        ts = row.find_all(["th", "td"])
        if len(ts) < 2:
            continue

        key = ts[0].get_text(strip=True)
        value = ts[1].get_text(strip=True)

        def parse_dividend(val: str, type: str) -> list[DividendRecord]:
            records: list[DividendRecord] = []
            if type == "cash":
                pattern = re.compile(
                    r"(?i)(\d+(?:\.\d+)?)%\s*(?:Cash)?(?:\s*(Final|Interim))?\s*(\d{2,4})?"
                )
            else:
                pattern = re.compile(
                    r"(?i)(\d+(?:\.\d+)?)%\s*(?:Bonus|Stock Dividend)?(?:\s*(Final|Interim))?\s*(\d{2,4})?"
                )

            matches = pattern.findall(val)
            for match in matches:
                percent_str, label, year_str = match
                percent = parse_percentage(percent_str) or 0.0
                year = int(year_str) if year_str.isdigit() else None
                if year:
                    if year < 30:
                        year += 2000
                    elif year < 100:
                        year += 1900
                records.append(
                    DividendRecord(
                        percentage=percent,
                        label=label if label else type.title(),
                        year=year or -1,
                    )
                )
            return records

        def parse_right_issue(val: str) -> list[RightIssueRecord]:
            records: list[RightIssueRecord] = []
            patterns = re.compile(
                r"(?i)(\d+R:\d+)(?:\s*@?\s*(?:Tk|BDT)?\s*([\d.]+|at par))?(?:,?\s*(\d{4}))?"
            )
            matches = patterns.findall(val)
            for match in matches:
                ratio, price, year_str = match
                year = int(year_str) if year_str.isdigit() else None
                if year:
                    if year < 30:
                        year += 2000
                    elif year < 100:
                        year += 1900
                records.append(
                    RightIssueRecord(
                        ratio=ratio,
                        price=price if price else None,
                        year=year or -1,
                    )
                )
            return records

        if "Cash Dividend" in key:
            basic_info["cash_dividends"] = parse_dividend(value, "cash")
        elif "Bonus Issue" in key:
            basic_info["bonus_issues"] = parse_dividend(value, "bonus")
        elif "Right Issue" in key:
            basic_info["right_issue"] = parse_right_issue(value)
        elif "Year End" in key:
            basic_info["year_end"] = value
        elif "Reserve & Surplus" in key:
            basic_info["reserve_surplus_mn"] = parse_number(value)
        elif "Other Comprehensive Income" in key or "OCI" in key:
            basic_info["oci_mn"] = parse_number(value)

    return basic_info


def parse_interim_financial_performance(
    soup: BeautifulSoup,
) -> InterimFinancialPerformance:
    """Parse interim financial performance section."""
    interim_data = {
        "year": None,
        "q1": {},
        "q2": {},
        "half_yearly": {},
        "q3": {},
        "nine_months": {},
        "annual": {},
    }

    fields = [
        "q1",
        "q2",
        "half_yearly",
        "q3",
        "nine_months",
        "annual",
    ]
    data = {field: {} for field in fields}

    h2_tags = soup.find_all("h2")

    for h2 in h2_tags:
        header_text = h2.get_text(strip=True)
        if "Interim Financial Performance" in header_text:
            year_match = re.search(r"\d{4}", header_text)
            if year_match:
                interim_data["year"] = int(year_match.group())

            table = h2.find_next("table")
            if table:
                # rows = table.find_all("tr")
                rows = extract_rows(table, "tr:not(.header)")
                # print("Interim Rows:", rows)
                for ri, row in enumerate(rows):
                    cells = row[1:]
                    for i, field in enumerate(fields):
                        if i < len(cells):
                            if ri == 0:
                                key = "eps_basic"
                                if cells[i] and cells[i] != "-":
                                    data[field][key] = parse_number(cells[i])
                            elif ri == 1:
                                key = "eps_diluted"
                                if cells[i] and cells[i] != "-":
                                    data[field][key] = parse_number(cells[i])
                            elif ri == 2:
                                key = "eps_continuing_basic"
                                if cells[i] and cells[i] != "-":
                                    data[field][key] = parse_number(cells[i])
                            elif ri == 3:
                                key = "eps_continuing_diluted"
                                if cells[i] and cells[i] != "-":
                                    data[field][key] = parse_number(cells[i])
                            elif ri == 4:
                                key = "market_price"
                                if cells[i] and cells[i] != "-":
                                    data[field][key] = parse_number(cells[i])

            break

    for field in fields:
        interim_data[field] = data.get(field, {})

    return InterimFinancialPerformance(**interim_data)


def _parse_pe_ratios(table: Tag) -> list[PERatioEntry]:
    """Parse P/E ratio sections."""
    rows = table.find_all("tr")
    data = []
    if len(rows) > 1:
        # Get date headers
        header_row = rows[0]
        date_cells = header_row.find_all("td")
        dates = []

        for cell in date_cells[1:]:
            date = parse_date(cell.get_text(strip=True))
            if date:
                dates.append(date)

        # Get P/E values
        for row in rows[1:]:
            cells = row.find_all("td")
            if cells:
                metric = cells[0].get_text(strip=True)
                values = [parse_number(c.get_text(strip=True)) for c in cells[1:]]

                for date, value in zip(dates, values, strict=False):
                    if date and value is not None:
                        data.append(
                            PERatioEntry(
                                date=date,
                                metric=metric,
                                value=value,
                            )
                        )

    return data


def parse_pe_ratios(soup: BeautifulSoup) -> PERatios:
    """Parse P/E ratio sections."""
    pe_data = {"unaudited": [], "audited": []}

    h2_tags = soup.find_all("h2")

    for h2 in h2_tags:
        header_text = h2.get_text(strip=True)
        if (
            "Un-audited Financial Statements" in header_text
            or "Audited Financial Statements" in header_text
        ):
            table = h2.find_next("table")
            if table:
                entries = _parse_pe_ratios(table)
                if "Un-audited Financial Statements" in header_text:
                    pe_data["unaudited"].extend(entries)
                elif "Audited Financial Statements" in header_text:
                    pe_data["audited"].extend(entries)

    return PERatios(**pe_data)


def extract_year(cells: list[str]) -> int | None:
    for c in cells[:3]:
        if c.isdigit() and len(c) == 4:
            return int(c)
    return None


def extract_rows(table, selector: str | None = None) -> list[list[str]]:
    rows = []
    for tr in table.select(selector or "tr.shrink, tr.shrink.alt"):
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        # if any(td.isdigit() and len(td) == 4 for td in tds):
        rows.append(tds)
    return rows


def parse_financial_performance(soup: BeautifulSoup) -> FinancialPerformance:
    h2_tags = soup.find_all("h2")
    tables = []
    audited_by = ""
    for h2 in h2_tags:
        htext = h2.get_text(strip=True)
        if "Financial Performance as per Audited" in htext:
            table = h2.find_next("table")
            if table:
                tables.append(table)
            parts = htext.split("as per")
            audited_by = parts[-1].strip() if len(parts) > 1 else ""

        if "Financial Performance..." in htext:
            table = h2.find_next("table")
            if table:
                tables.append(table)
        if len(tables) >= 2:
            break

    if len(tables) < 2:
        return FinancialPerformance(
            statements=[],
            financial_statement_url=None,
            price_sensitive_info_url=None,
            audited_by=audited_by,
        )

    financials: dict[int, dict[str, Any]] = {}

    # ---------- TABLE 1 ----------
    rows = extract_rows(tables[0])
    for cells in rows:
        year = extract_year(cells)
        if not year:
            continue

        # Adjust indexes: after year (colspan=2)
        data_cells = cells[1:] if cells[0] == str(year) else cells[2:]

        fields = [
            "eps_basic_original",
            "eps_basic_restated",
            "eps_diluted",
            "eps_continuing_basic_original",
            "eps_continuing_basic_restated",
            "eps_continuing_diluted",
            "nav_per_share_original",
            "nav_per_share_restated",
            "nav_per_share_diluted",
            "profit_continuing_mn",
            "profit_for_year_mn",
            "total_comprehensive_income_mn",
        ]

        data: dict[str, Any] = {"year": year}
        for i, field in enumerate(fields):
            if i < len(data_cells):
                data[field] = parse_number(data_cells[i])
        financials[year] = data

    # ---------- TABLE 2 ----------
    rows = extract_rows(tables[1])
    for cells in rows:
        year = extract_year(cells)
        if not year:
            continue

        data_cells = cells[1:] if cells[0] == str(year) else cells[2:]

        fields = [
            "pe_ratio_basic_original",
            "pe_ratio_basic_restated",
            "pe_ratio_diluted",
            "pe_continuing_basic_original",
            "pe_continuing_basic_restated",
            "pe_continuing_diluted",
            "dividend_percent",
            "dividend_yield_percent",
        ]

        entry = financials.get(year, {"year": year})
        for i, field in enumerate(fields):
            if i < len(data_cells):
                val = data_cells[i]
                if field.startswith("dividend"):
                    if field == "dividend_percent":
                        entry[field] = parse_percentage(val)
                        entry["dividend_type"] = "Bonus" if "B" in val else "Cash"
                    else:
                        entry[field] = parse_percentage(val)
                else:
                    entry[field] = parse_number(val)
        financials[year] = entry

    url_table = tables[1].find_next("table")
    financial_statement_url = None
    price_sensitive_info_url = None
    if url_table:
        trs = url_table.find_all("tr")
        for tr in trs:
            th = tr.find("th")
            td = tr.find("td")
            if th and td:
                link = td.find("a")
                href = link.get("href") if link else None
                if "Financial Statement" in th.get_text(strip=True):
                    financial_statement_url = str(href) if href else None
                elif "Price Sensitive Information" in th.get_text(strip=True):
                    price_sensitive_info_url = str(href) if href else None

    # sort financials by year descending
    statements = [
        FinancialPerformanceAudited(**financials[year])
        for year in sorted(financials.keys(), reverse=True)
    ]
    return FinancialPerformance(
        statements=statements,
        financial_statement_url=financial_statement_url,
        price_sensitive_info_url=price_sensitive_info_url,
        audited_by=audited_by,
    )


def parse_other_information(table: Tag) -> OtherInformation:
    """Parse other information section including listing, shareholding, etc."""
    other_info: dict[str, Any] = {
        "listing_year": None,
        "market_category": None,
        "electronic_share": None,
        "remarks": None,
        "shareholding": [],
    }

    rows = table.find_all("tr")

    for row in rows:
        first_cell = row.find("td")
        if not first_cell:
            continue

        text = first_cell.get_text(strip=True)
        cells = row.find_all("td")

        parse_map = {
            "Listing Year": "listing_year",
            "Market Category": "market_category",
            "Electronic Share": "electronic_share",
            "Remarks": "remarks",
        }
        for k, v in parse_map.items():
            if k in text and len(cells) >= 2:
                value = cells[1].get_text(strip=True)
                if v == "listing_year":
                    if value and value != "-":
                        other_info[v] = int(value)
                else:
                    other_info[v] = value if value and value != "-" else None
                break

        # Parse shareholding
        if "Share Holding Percentage" in text:
            # Extract date from text
            date_match = re.search(r"as on ([A-Za-z]+ \d+, \d+)", text)

            # Get shareholding table
            nested_table = row.find("table")
            if nested_table:
                nested_row = nested_table.find("tr")
                if nested_row:
                    nested_cells = nested_row.find_all("td")

                    holding_data = {
                        "date": parse_date(date_match.group(1)) if date_match else None,
                        "sponsor_director": None,
                        "govt": None,
                        "institute": None,
                        "foreign": None,
                        "public": None,
                    }
                    parse_map = {
                        "Sponsor/Director:": "sponsor_director",
                        "Govt:": "govt",
                        "Institute:": "institute",
                        "Foreign:": "foreign",
                        "Public:": "public",
                    }

                    for k, v in parse_map.items():
                        for cell in nested_cells:
                            cell_text = cell.get_text(strip=True)
                            if k in cell_text:
                                holding_data[v] = parse_number(cell_text.split(":")[1])
                                break

                    other_info["shareholding"].append(ShareholdingEntry(**holding_data))

    return OtherInformation(**other_info)


def parse_corporate_performance(table: Tag) -> CorporatePerformance:
    """Parse corporate performance section."""
    performance: dict[str, Any] = {
        "operational_status": None,
        "short_term_loan_mn": None,
        "long_term_loan_mn": None,
        "latest_dividend": None,
        "credit_rating_short_term": None,
        "credit_rating_long_term": None,
        "otc_delisting_relisting": None,
    }

    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            key = cells[-2].get_text(strip=True) if len(cells) >= 2 else ""
            value = cells[-1].get_text(strip=True) if len(cells) >= 1 else ""

            if "Operational Status" in key or "Present Operational Status" in key:
                performance["operational_status"] = value if value else None
            elif "Short-term loan" in key:
                performance["short_term_loan_mn"] = parse_number(value)
            elif "Long-term loan" in key:
                performance["long_term_loan_mn"] = parse_number(value)
            elif "Latest Dividend Status" in key:
                performance["latest_dividend"] = value if value else None
            elif "Short-term" in key and len(cells) == 2:
                # Credit rating short-term
                performance["credit_rating_short_term"] = value if value else None
            elif "Long-term" in key and len(cells) == 2:
                # Credit rating long-term
                performance["credit_rating_long_term"] = value if value else None
            elif "OTC/Delisting/Relisting" in key:
                performance["otc_delisting_relisting"] = value if value else None

    return CorporatePerformance(**performance)


def parse_company_address(table: Tag) -> CompanyAddress:
    """Parse company address and contact information."""
    address_info: dict[str, Any] = {}
    rows = table.find_all("tr")

    scaler_keys_map = {
        "Head Office": "head_office",
        "Factory": "factory",
        "Contact Phone": "phone",
        "Fax": "fax",
        "Company Secretary Name": "company_secretary",
    }
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            # Get key from second-to-last cell
            key = cells[-2].get_text(strip=True)
            value = cells[-1].get_text(strip=True)

            for k in scaler_keys_map:
                if k in key:
                    address_info[scaler_keys_map[k]] = value if value else None
                    break

            if "Web Address" in key:
                link = cells[-1].find("a")
                if link:
                    href = link.get("href")
                    address_info["website"] = str(href) if href else value
                else:
                    address_info["website"] = value
            elif "Cell No." in key:
                # Check if this is secretary's cell
                prev_rows = [r.get_text() for r in row.find_previous_siblings("tr")[:2]]
                if any("Secretary" in r for r in prev_rows):
                    address_info["secretary_cell"] = value
            elif "Telephone No." in key:
                # Check if this is secretary's telephone
                prev_rows = [r.get_text() for r in row.find_previous_siblings("tr")[:3]]
                if any("Secretary" in r for r in prev_rows):
                    address_info["secretary_telephone"] = value
            elif "E-mail" in key:
                # Check if this is secretary's email or company email
                prev_rows = [r.get_text() for r in row.find_previous_siblings("tr")[:4]]
                if any("Secretary" in r for r in prev_rows):
                    address_info["secretary_email"] = value
                elif "email" not in address_info:
                    address_info["email"] = value

    return CompanyAddress(**address_info)


def parse_dse_company_data(soup: BeautifulSoup) -> DSECompanyData:
    """
    Main function to parse DSE company information page.

    Args:
        soup: BeautifulSoup object of the HTML page

    Returns:
        DSECompanyData containing all parsed company information
    """

    h2_tags = soup.find_all("h2")

    # Parse sections that don't require table iteration
    financial_performance = parse_financial_performance(soup)
    interim_financial_performance = parse_interim_financial_performance(soup)
    pe_ratios = parse_pe_ratios(soup)

    # Initialize basic information dict
    basic_info_dict: dict[str, Any] = {}
    market_information = None
    other_information = None
    corporate_performance = None
    address = None

    for h2 in h2_tags:
        htext = h2.get_text(strip=True)
        table = h2.find_next("table")
        if not table:
            continue
        if "Company Name:" in htext:
            basic_info_dict.update(parse_company_basic_info(table, h2))
        elif "Address of the Company" in htext:
            address = parse_company_address(table)
        elif "Corporate Performance at a glance" in htext:
            corporate_performance = parse_corporate_performance(table)
        elif "Other Information" in htext:
            other_information = parse_other_information(table)
        elif "Market Information" in htext:
            market_information = parse_market_information(table, h2)
        elif "Basic Information" in htext:
            basic_info_dict.update(parse_basic_information(table))

    # Create BasicInformation model
    basic_information = BasicInformation(**basic_info_dict)

    return DSECompanyData(
        basic_information=basic_information,
        market_information=market_information or MarketInformation(),
        financial_performance=financial_performance,
        interim_financial_performance=interim_financial_performance,
        pe_ratios=pe_ratios,
        other_information=other_information
        or OtherInformation(
            shareholding=[],
            market_category="A",
            listing_year=2001,
            electronic_share="P",
        ),
        corporate_performance=corporate_performance or CorporatePerformance(),
        address=address
        or CompanyAddress(
            head_office="",
            phone="",
            email="",
            website="",
            company_secretary="",
        ),
    )

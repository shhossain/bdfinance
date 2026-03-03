"""Centralized data cleaning utilities for parsing DSE data

This module provides reusable functions for cleaning and normalizing
data from DSE sources. All cleaning logic should be centralized here
to ensure consistency across all parsers and models.
"""

from datetime import datetime
from typing import Any


def clean_text(value: Any) -> str:
    """Clean and normalize text values"""
    if value is None:
        return ""
    return str(value).strip()


def clean_float(value: Any, default: float = 0.0) -> float:
    """
    Clean and convert value to float, handling common edge cases

    Handles:
    - Comma-separated numbers: "1,234.56"
    - Missing values: "n/a", "N/A", "-", "--", ""
    - Already numeric values
    - Negative numbers (preserves sign)

    Args:
        value: Raw value to clean
        default: Default value if parsing fails

    Returns:
        Cleaned float value
    """
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return default

    # Remove commas and whitespace
    cleaned = value.replace(",", "").strip()

    # Handle missing/invalid values
    if cleaned in ("", "n/a", "N/A", "-", "--"):
        return default

    # Try to convert to float
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return default


def clean_int(value: Any, default: int = 0) -> int:
    """
    Clean and convert value to int, handling common edge cases

    Handles:
    - Comma-separated numbers: "1,234"
    - Missing values: "n/a", "N/A", "-", "--", ""
    - Already numeric values

    Args:
        value: Raw value to clean
        default: Default value if parsing fails

    Returns:
        Cleaned integer value
    """
    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if not isinstance(value, str):
        return default

    # Remove commas and whitespace
    cleaned = value.replace(",", "").strip()

    # Handle missing/invalid values
    if cleaned in ("", "n/a", "N/A", "-", "--"):
        return default

    # Try to convert to int
    try:
        # Handle floats in strings
        return int(float(cleaned))
    except (ValueError, TypeError):
        return default


def clean_percent(value: Any) -> float:
    """
    Clean percentage string to float

    Handles:
    - "15%" -> 15.0
    - "15.5%" -> 15.5
    - "15" -> 15.0

    Args:
        value: Raw percentage value

    Returns:
        Percentage as float (without % sign)
    """
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return 0.0

    cleaned = value.replace("%", "").strip()
    return clean_float(cleaned)


def clean_symbol(value: Any) -> str:
    """
    Clean and normalize stock symbol

    Args:
        value: Raw symbol value

    Returns:
        Uppercase, stripped symbol
    """
    if not value:
        return ""
    return str(value).strip().upper()


def clean_date(value: Any, format: str = "%Y-%m-%d") -> datetime:
    """
    Clean date string

    Args:
        value: Raw date value

    Returns:
        Cleaned date string
    """
    d = str(value).strip()
    date = datetime.strptime(d, format)
    return date


def parse_market_value(value: Any) -> float:
    """
    Parse market value strings that may include units (mn, bn, cr)

    Handles:
    - "1,234.56 mn" -> 1234.56
    - "1.5 bn" -> 1500.0
    - "100 cr" -> 10000.0

    Args:
        value: Raw market value

    Returns:
        Value in millions
    """
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        return 0.0

    value_str = value.lower().strip()

    # Extract numeric part
    numeric_part = ""
    unit = ""

    for char in value_str:
        if char.isdigit() or char in ".,- ":
            numeric_part += char
        else:
            unit += char

    num = clean_float(numeric_part.strip())

    # Apply multiplier based on unit
    if "bn" in unit or "billion" in unit:
        return num * 1000  # Convert to millions
    elif "cr" in unit or "crore" in unit:
        return num * 10  # 1 crore = 10 million
    else:
        return num


def extract_tenor_from_symbol(symbol: str) -> str:
    """
    Extract bond tenor from a treasury bond symbol.

    Args:
        symbol: Bond trading symbol (e.g. 'TB10Y0634')

    Returns:
        Tenor string like '10Y', '5Y', '2Y', '15Y', '20Y', or '10Y' as default
    """
    for t in ["20Y", "15Y", "10Y", "5Y", "2Y"]:
        if f"TB{t}" in symbol:
            return t
    return "10Y"


def compute_approx_ytm(
    coupon: float,
    face: float,
    price: float,
    maturity_date_str: str,
) -> float | None:
    """
    Compute approximate yield-to-maturity for a bond.

    Uses the approximation formula:
        YTM ≈ (C + (F - P) / n) / ((F + P) / 2) × 100

    Args:
        coupon: Annual coupon rate (in currency units, not percent)
        face: Face/par value
        price: Current market price
        maturity_date_str: Maturity date as a string (parseable by dateutil)

    Returns:
        Approximate YTM as a percentage, or None if not computable
    """
    if price <= 0 or not maturity_date_str:
        return None

    try:
        from dateutil.parser import parse as dateutil_parse

        mat_dt = dateutil_parse(maturity_date_str)
        years_to_mat = (mat_dt - datetime.now()).days / 365.25
        if years_to_mat <= 0:
            return None
        return round(
            (coupon + (face - price) / years_to_mat) / ((face + price) / 2) * 100,
            2,
        )
    except (ValueError, TypeError):
        return None

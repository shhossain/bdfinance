from datetime import datetime, timedelta


def period_parsing(period: str) -> timedelta:
    """Convert period string to timedelta"""
    period = period.lower()
    if period.endswith("mo"):
        months = int(period[:-2])
        return timedelta(days=30 * months)
    elif period.endswith("y"):
        years = int(period[:-1])
        return timedelta(days=365 * years)
    elif period.endswith("d"):
        days = int(period[:-1])
        return timedelta(days=days)
    else:
        raise ValueError("Invalid period format. Use '1mo', '1y', '30d', etc.")


def convert_to_start_end_date(
    start: str | None | datetime,
    end: str | None | datetime,
    period: str | timedelta | None = None,
    default_period: str = "30d",
    format: str = "%Y-%m-%d",
) -> tuple[str, str]:
    end_date = datetime.now()
    if period:
        if isinstance(period, timedelta):
            delta = period
        else:
            delta = period_parsing(period)
        delta = period_parsing(period)
    else:
        delta = period_parsing(default_period)
    start_date = end_date - delta

    if isinstance(start, datetime):
        start_str = start.strftime(format)
    elif isinstance(start, str):
        start_str = start
    else:
        start_str = start_date.strftime(format)
    if isinstance(end, datetime):
        end_str = end.strftime(format)
    elif isinstance(end, str):
        end_str = end
    else:
        end_str = end_date.strftime(format)
    return start_str, end_str

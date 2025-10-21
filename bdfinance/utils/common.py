from collections.abc import Sequence
from typing import Any, Optional


def make_lower_case(s: str) -> str:
    """Convert a string to lower case.

    Args:
        s (str): The input string.

    Returns:
        str: The lower-cased string.
    """
    return s.lower().replace(" ", "_").replace("-", "_")


def convert_dict_keys_to_lower(d: dict) -> dict:
    """Convert all keys in a dictionary to lower case.

    Args:
        d (dict): The input dictionary.

    Returns:
        dict: A new dictionary with all keys converted to lower case.
    """
    return {make_lower_case(k): v for k, v in d.items()}


def adapt_dict_values(d: Any) -> Any:
    """Convert dictionary values to appropriate types.

    Args:
        d (dict): The input dictionary.

    Returns:
        dict: A new dictionary with values converted to appropriate types.
    """
    if isinstance(d, dict):
        for k, v in d.items():
            d[k] = adapt_dict_values(v)
        return d
    elif isinstance(d, str):
        if "." in d:
            try:
                return float(d.replace(",", ""))
            except ValueError:
                return d
        elif d.replace(",", "").isdigit():
            return int(d.replace(",", ""))
        elif d.lower() in {"true", "false"}:
            return d.lower() == "true"
    elif isinstance(d, Sequence):
        return [adapt_dict_values(i) for i in d]

    return d

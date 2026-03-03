"""HTML parsing utilities for extracting data from DSE pages"""

from collections.abc import Callable
from typing import Any

import structlog
from bs4 import BeautifulSoup, Tag

from bdfinance.utils.common import adapt_dict_values
from bdfinance.utils.data_cleaners import (
    clean_date,
    clean_float,
    clean_int,
    clean_symbol,
    clean_text,
)
from bdfinance.utils.parse_com_info import parse_dse_company_data

logger = structlog.get_logger()


class HTMLParser:
    """HTML parser for DSE data extraction"""

    @staticmethod
    def parse_table_to_dicts(
        html: str,
        table_selector: dict[str, Any],
        skip_rows: int = 1,
        column_mapping: dict[int, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Parse HTML table to list of dictionaries"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", attrs=table_selector)

        if not table:
            logger.warning("Table not found", selector=table_selector)
            return []

        rows = table.find_all("tr")[skip_rows:]
        results = []

        for row in rows:
            cols = row.find_all("td")
            if not cols:
                continue

            if column_mapping:
                row_data = {}
                for col_idx, col_name in column_mapping.items():
                    if col_idx < len(cols):
                        row_data[col_name] = cols[col_idx].text.strip()
                results.append(row_data)

        return results

    @staticmethod
    def parse_current_trade_data(html: str) -> list[dict[str, Any]]:
        """Parse current trade data table"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find(
            "table",
            attrs={
                "class": "table table-bordered background-white shares-table fixedHeader"
            },
        )

        if not table:
            logger.warning("Current trade data table not found")
            return []

        quotes = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 11:
                continue

            quotes.append(
                {
                    "Symbol": clean_symbol(cols[1].text),
                    "LTP": clean_float(cols[2].text),
                    "High": clean_float(cols[3].text),
                    "Low": clean_float(cols[4].text),
                    "Close": clean_float(cols[5].text),
                    "YCP": clean_float(cols[6].text),
                    "Change": clean_float(cols[7].text),
                    "Trade": clean_int(cols[8].text),
                    "Value": clean_float(cols[9].text),
                    "Volume": clean_int(cols[10].text),
                }
            )

        return quotes

    @staticmethod
    def parse_index_data(html: str) -> list[dict[str, Any]]:
        """Parse index data table"""
        soup = BeautifulSoup(html, "lxml")
        tables = soup.select("#RightBody table")
        data = []
        # Market Summary of Oct 14, 2025
        for table in tables:
            trs = table.find_all("tr")
            header = trs[0]
            date = header.get_text(strip=True).replace("Market Summary of ", "")
            date = clean_date(date, format="%b %d, %Y")
            d = {}
            for row in trs[1:]:
                tds = row.find_all("td")
                chunked = [tds[i : i + 2] for i in range(0, len(tds), 2)]
                for pair in chunked:
                    if len(pair) == 2:
                        key = clean_text(pair[0].get_text(strip=True))
                        value = clean_text(pair[1].get_text(strip=True))
                        d[key] = value
            d["Date"] = date
            d["Symbol"] = "DSEX"

            parse_map = {
                "DSEX Index": ("DSEX", clean_float),
                "DSEX Index Change": ("DSEX Change", clean_float),
                "DS30 Index": ("DS30", clean_float),
                "DS30 Index Change": ("DS30 Change", clean_float),
                "Total Trade": ("Trade", clean_int),
                "Total Value Taka(mn)": ("Value", clean_float),
                "Total Volume": ("Volume", clean_int),
                "Total Market Cap. Taka(mn)": ("Market Cap", clean_float),
            }

            for key, (new_key, func) in parse_map.items():
                if key in d:
                    d[new_key] = func(d[key])
                    if new_key != key:
                        del d[key]

            data.append(d)

        return data

    @staticmethod
    def parse_historical_data(html: str) -> list[dict[str, Any]]:
        """Parse historical trading data table"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find(
            "table",
            attrs={
                "class": "table table-bordered background-white shares-table fixedHeader"
            },
        )

        if not table:
            logger.warning("Historical data table not found")
            return []

        quotes = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 12:
                continue

            quotes.append(
                {
                    # 2025-10-15
                    "Date": clean_date(cols[1].text, format="%Y-%m-%d"),
                    "Symbol": clean_symbol(cols[2].text),
                    "LTP": clean_float(cols[3].text),
                    "High": clean_float(cols[4].text),
                    "Low": clean_float(cols[5].text),
                    "Open": clean_float(cols[6].text),
                    "Close": clean_float(cols[7].text),
                    "YCP": clean_float(cols[8].text),
                    "Trade": clean_int(cols[9].text),
                    "Value": clean_float(cols[10].text),
                    "Volume": clean_int(cols[11].text),
                }
            )

        return quotes

    @staticmethod
    def parse_market_info(html: str):
        """Parse market information table"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.select_one("table[_id='data-table']")
        if not table:
            logger.warning("Market info table not found")
            return []

        data = HTMLParser.parse_simple_table(
            table,
            mappings={
                "TotalValuein Taka(mn)": "Value",
                "TotalMarket Cap.in Taka (mn)": "Market Cap",
                "TotalTrade": "Trade",
                "TotalVolume": "Volume",
                "DSEXIndex": "DSEX",
                "DSESIndex": "DSES",
                "DS30Index": "DS30",
                "DGENIndex": "DGEN",
            },
            transform_values={
                "Date": lambda x: clean_date(x, format="%d-%m-%Y"),
            },
        )
        if data:
            data = adapt_dict_values(data)
        return data

    @staticmethod
    def parse_latest_pe(html: str):
        """Parse latest P/E table"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find(
            "table",
            attrs={
                "class": "table table-bordered background-white shares-table fixedHeader"
            },
        )

        if not table:
            logger.warning("Latest PE table not found")
            return []

        # quotes = []
        # for row in table.find_all("tr")[1:]:
        #     cols = row.find_all("td")
        #     if len(cols) < 10:
        #         continue

        #     quotes.append(
        #         {
        #             "Symbol": clean_symbol(cols[1].text),
        #             "Close": clean_float(cols[2].text),
        #             "YCP": clean_float(cols[3].text),
        #             "P/E 1": clean_float(cols[4].text),
        #             "P/E 2": clean_float(cols[5].text),
        #             "P/E 3": clean_float(cols[6].text),
        #             "P/E 4": clean_float(cols[7].text),
        #             "P/E 5": clean_float(cols[8].text),
        #             "P/E 6": clean_float(cols[9].text),
        #         }
        #     )

        # return quotes

        # aders=['#', 'Trade Code', 'Close Price', 'YCP', 'P/E 1*(Basic)', 'P/E 2*(Diluted)', 'P/E 3*(Basic)', 'P/E 4*(Diluted)', 'P/E 5*', 'P/E 6*']
        data = HTMLParser.parse_simple_table(
            table,
            mappings={
                "Trade Code": "Symbol",
                "Close Price": "Close",
                "YCP": "YCP",
                "P/E 1*(Basic)": "P/E 1",
                "P/E 2*(Diluted)": "P/E 2",
                "P/E 3*(Basic)": "P/E 3",
                "P/E 4*(Diluted)": "P/E 4",
                "P/E 5*": "P/E 5",
                "P/E 6*": "P/E 6",
            },
            remove_cols=["#"],
            transform_values={
                "Symbol": clean_symbol,
                "Close": clean_float,
                "YCP": clean_float,
                "P/E 1": clean_float,
                "P/E 2": clean_float,
                "P/E 3": clean_float,
                "P/E 4": clean_float,
                "P/E 5": clean_float,
                "P/E 6": clean_float,
            },
            add_links=False,
        )
        if data:
            data = adapt_dict_values(data)
        return data

    @staticmethod
    def parse_agm_news(html: str) -> list[dict[str, Any]]:
        """Parse AGM news table"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")

        if not table:
            logger.warning("AGM news table not found")
            return []

        news = []
        for row in table.find_all("tr")[4:-6]:
            cols = row.find_all("td")
            if len(cols) < 7:
                continue

            news.append(
                {
                    "Company": clean_text(cols[0].text.strip()),
                    "Year End": clean_text(cols[1].text),
                    "Dividend": clean_text(cols[2].text),
                    "Date of AGM/EGM": clean_text(cols[3].text),
                    "Record Date": clean_text(cols[4].text),
                    "Venue": clean_text(cols[5].text),
                    "Time": clean_text(cols[6].text),
                }
            )

        return news

    @staticmethod
    def parse_news(html: str) -> list[dict[str, Any]]:
        """Parse general news"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", attrs={"class": "table-news"})

        if not table:
            logger.warning("News table not found")
            return []

        news_items = []
        current_item: dict[str, Any] = {}

        for row in table.find_all("tr"):
            heads = row.find_all("th")
            cols = row.find_all("td")

            if not heads or not cols:
                continue

            header_text = heads[0].text.strip()

            if header_text == "News Title:":
                if current_item:
                    news_items.append(current_item)
                current_item = {"News Title": cols[0].text.strip()}
            elif header_text == "News:":
                current_item["News"] = cols[0].text.strip()
            elif header_text == "Post Date:":
                current_item["Post Date"] = cols[0].text.strip()

        if current_item:
            news_items.append(current_item)

        return news_items

    @staticmethod
    def parse_market_depth(html: str) -> list[dict[str, Any]]:
        """Parse market depth data"""
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", attrs={"class": "table table-stripped"})

        if not table:
            logger.warning("Market depth table not found")
            return []

        result = []
        matrix = ["buy_price", "buy_volume", "sell_price", "sell_volume"]

        for row in table.find_all("tr")[:1]:
            cols = row.find_all("td", valign="top")
            index = 0

            for mainrow in cols:
                for subrow in mainrow.find_all("tr")[2:]:
                    newcols = subrow.find_all("td")
                    if len(newcols) >= 2:
                        result.append(
                            {
                                matrix[index]: newcols[0].text.strip(),
                                matrix[index + 1]: newcols[1].text.strip(),
                            }
                        )
                index = index + 2

        return result

    @staticmethod
    def parse_table_rows(trs: list[Tag]) -> list[dict[str, Any]]:
        """Parse back to back data from table rows"""
        results = []
        for row in trs:
            prev_title = ""
            d = {}
            flag = 0
            for t in row.find_all(["th", "td"]):
                if flag == 0:
                    prev_title = t.text.strip().replace(":", "")
                    flag = 1
                else:
                    d[prev_title] = t.text.strip()
                    flag = 0
            results.append(d)
        return results

    @staticmethod
    def parse_company_info(html: str):
        """Parse company info tables using pandas"""
        soup = BeautifulSoup(html, "lxml")
        info = parse_dse_company_data(soup)
        return info

    @staticmethod
    def parse_simple_table(
        table: Tag,
        add_links: bool = True,
        mappings: dict[str, Any] | None = None,
        transform_keys: Callable[[str], Any] | None = None,
        transform_values: dict[str, Callable[[Any], Any]] | None = None,
        remove_cols: list[str] | None = None,
    ) -> list[dict[str, Any]] | None:
        """Parse simple key-value table"""
        rows = table.find_all("tr")
        data = []
        headers = []
        idx = 0
        if rows:
            headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
            idx = 1

        logger.debug("Parsing simple table", headers=headers, rows=len(rows))

        link_suffix = "_Link"
        for row in rows[idx:]:
            cols = row.find_all("td")
            d = {}
            if headers:
                for header, col in zip(headers, cols, strict=False):
                    d[header] = col.get_text(strip=True)
                    atag = col.find("a")
                    if add_links and atag and atag.has_attr("href"):
                        d[f"{header}{link_suffix}"] = atag["href"]
            else:
                for i, col in enumerate(cols):
                    d[f"col_{i}"] = col.get_text(strip=True)
                    atag = col.find("a")
                    if add_links and atag and atag.has_attr("href"):
                        d[f"col_{i}{link_suffix}"] = atag["href"]
            data.append(d)

        if mappings:
            for item in data:
                for old_key, new_key in mappings.items():
                    if old_key in item:
                        if (
                            isinstance(new_key, tuple)
                            and len(new_key) == 2
                            and callable(new_key[1])
                        ):
                            item[new_key[0]] = new_key[1](item.pop(old_key))
                            if f"{old_key}{link_suffix}" in item:
                                item[f"{new_key[0]}{link_suffix}"] = item.pop(
                                    f"{old_key}{link_suffix}"
                                )
                        else:
                            item[new_key] = item.pop(old_key)
                            if f"{old_key}{link_suffix}" in item:
                                item[f"{new_key}{link_suffix}"] = item.pop(
                                    f"{old_key}{link_suffix}"
                                )

        if transform_keys:
            # for keys
            for item in data:
                for key in list(item.keys()):
                    item[transform_keys(key)] = item.pop(key)

        if transform_values:
            for item in data:
                for key, func in transform_values.items():
                    if key in item and callable(func):
                        item[key] = func(item[key])

        if remove_cols:
            for item in data:
                for col in remove_cols:
                    item.pop(col, None)
                    item.pop(f"{col}{link_suffix}", None)

        return data

    @staticmethod
    def parse_sector_list(html: str):
        mappings = {"Name of the Industry": "Sector", "Sector_Link": "Code"}
        selector = "#RightBody table"
        soup = BeautifulSoup(html, "lxml")
        table = soup.select_one(selector)

        if not table:
            logger.warning("Simple table not found", selector=selector)
            return None

        data = HTMLParser.parse_simple_table(
            table,
            mappings=mappings,
            remove_cols=["#", "Detail"],
            transform_values={"Code": lambda x: x.split("=")[-1].strip() if x else x},
        )
        if data:
            data.pop()
            data = adapt_dict_values(data)
        return data

    @staticmethod
    def parse_price_table(html: str):
        mappings = {
            "TRADING CODE": "Symbol",
            "Trade Code": "Symbol",
            "% CHANGE": "Change",
            "CLOSEP*": "Close",
        }
        selector = "#RightBody table"
        soup = BeautifulSoup(html, "lxml")
        table = soup.select_one(selector)
        if not table:
            logger.warning("Simple table not found", selector=selector)
            return None

        def transform(x):
            if x.endswith("*"):
                x = x.replace("*", "")
            if x.endswith("(mn)"):
                x = x.replace("(mn)", "").strip()
            x = x.upper() if len(x) <= 3 else x.lower().title()
            return x.strip()

        data = HTMLParser.parse_simple_table(
            table,
            add_links=False,
            mappings=mappings,
            transform_keys=transform,
            remove_cols=["#"],
        )
        if data:
            data = adapt_dict_values(data)
        return data

    @staticmethod
    def parse_latest_share_price(html: str):
        return HTMLParser.parse_price_table(html)

    @staticmethod
    def parse_top_stocks(html: str):
        return HTMLParser.parse_price_table(html)

    @staticmethod
    def parse_top_10(html: str):
        return HTMLParser.parse_price_table(html)

    @staticmethod
    def parse_tbond_info(html: str) -> dict[str, str]:
        """
        Parse treasury bond detail page to extract bond metadata.

        Extracts key-value pairs from th-td table rows such as
        Coupon Rate, Issue Date, Maturity Date, etc.

        Args:
            html: Raw HTML of the bond info page

        Returns:
            Dict of bond metadata fields
        """
        soup = BeautifulSoup(html, "lxml")
        info: dict[str, str] = {}

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                # Process pairs: (cells[0],cells[1]), (cells[2],cells[3]), ...
                for j in range(0, len(cells) - 1, 2):
                    key = cells[j].get_text(strip=True)
                    val = cells[j + 1].get_text(strip=True)
                    if key and val:
                        info[key] = val

        return info

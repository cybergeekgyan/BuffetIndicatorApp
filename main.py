# wb_buffett_helper.py
"""
Helper functions to download World Bank market cap and GDP, compute Buffett Indicator.
Uses World Bank API:
 - Market cap indicator: CM.MKT.LCAP.CD
 - GDP indicator:        NY.GDP.MKTP.CD
"""

import requests
import pandas as pd
from typing import List, Dict
import time

WB_API = "https://api.worldbank.org/v2"

# Top-10 country mapping (display name -> ISO3)
TOP10_COUNTRIES = {
    "United States": "USA",
    "China": "CHN",
    "Japan": "JPN",
    "India": "IND",
    "United Kingdom": "GBR",
    "France": "FRA",
    "Canada": "CAN",
    "Germany": "DEU",
    "Switzerland": "CHE",
    "Australia": "AUS"
}

MARKETCAP_IND = "CM.MKT.LCAP.CD"
GDP_IND = "NY.GDP.MKTP.CD"

def _fetch_indicator_for_country(country_iso3: str, indicator: str, start_year: int = 1990, end_year: int = None) -> pd.Series:
    """
    Fetch indicator from World Bank for a single country as a pd.Series indexed by year (int).
    Returns a Series of floats (values in current US$) with year index.
    """
    if end_year is None:
        end_year = pd.Timestamp.now().year
    per_page = 1000
    url = f"{WB_API}/country/{country_iso3}/indicator/{indicator}"
    params = {"date": f"{start_year}:{end_year}", "format": "json", "per_page": per_page}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    # data[1] is list of results; each item has 'date' and 'value'
    if not isinstance(data, list) or len(data) < 2:
        return pd.Series(dtype=float)
    records = data[1]
    values = {}
    for item in records:
        year = int(item["date"])
        val = item["value"]
        values[year] = float(val) if val is not None else None
    # Make series sorted by year ascending
    s = pd.Series(values).sort_index()
    s.index = s.index.astype(int)
    return s

def fetch_for_countries(countries: List[str], start_year: int = 1990, end_year: int = None, pause: float = 0.2) -> Dict[str, pd.DataFrame]:
    """
    For a list of country display names (must be keys in TOP10_COUNTRIES), fetch marketcap & GDP and
    return dictionary mapping country -> DataFrame with columns ['market_cap', 'gdp', 'buffett_indicator'].
    Buffett indicator returned as a decimal fraction (e.g. 1.23 -> 123%).
    """
    result = {}
    for name in countries:
        iso = TOP10_COUNTRIES.get(name)
        if iso is None:
            raise ValueError(f"Country '{name}' not in TOP10_COUNTRIES mapping.")
        mc = _fetch_indicator_for_country(iso, MARKETCAP_IND, start_year, end_year)
        gdp = _fetch_indicator_for_country(iso, GDP_IND, start_year, end_year)
        # align index (years)
        df = pd.DataFrame({"market_cap": mc, "gdp": gdp})
        # Buffett indicator: market_cap / gdp (as fraction, multiply by 100 for percent in display)
        df["buffett"] = df["market_cap"] / df["gdp"]
        result[name] = df
        time.sleep(pause)  # polite pause to avoid hammering API
    return result

def combine_countries_to_df(country_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combine country data dict into a multi-column DataFrame of buffett indicator (percent).
    Returns df where columns are country names and rows are years from the union of years.
    Values are in percent (i.e., buffett * 100).
    """
    frames = []
    for name, df in country_data.items():
        s = df["buffett"] * 100.0  # percent
        s.name = name
        frames.append(s)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, axis=1).sort_index()
    return combined

if __name__ == "__main__":
    # simple CLI example to test fetch
    countries = list(TOP10_COUNTRIES.keys())[:3]  # example first 3
    data = fetch_for_countries(countries)
    combined = combine_countries_to_df(data)
    print(combined.tail(10))

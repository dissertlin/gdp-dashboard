"""Data loading and calculation helpers for the GDP dashboard (no Streamlit)."""

from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).parent / 'data' / 'gdp_data.csv'
DEFAULT_COUNTRIES = ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN']


def reshape_gdp(raw: pd.DataFrame) -> pd.DataFrame:
    """Pivot wide year columns into long format: Country Name/Code, Year, GDP.

    Year columns are detected from the data, so new years need no code change.
    """
    year_cols = [c for c in raw.columns if str(c).strip().isdigit()]
    if not year_cols:
        raise ValueError('No year columns found in GDP data')
    df = raw.melt(['Country Name', 'Country Code'], year_cols, 'Year', 'GDP')
    df['Year'] = pd.to_numeric(df['Year']).astype(int)
    df['GDP'] = pd.to_numeric(df['GDP'], errors='coerce')
    return df


def load_gdp_data(path: Path = DATA_FILE) -> pd.DataFrame:
    return reshape_gdp(pd.read_csv(path))


def filter_gdp(df: pd.DataFrame, countries, from_year: int, to_year: int) -> pd.DataFrame:
    return df[
        df['Country Code'].isin(countries)
        & df['Year'].between(from_year, to_year)
    ]


def gdp_summary(df: pd.DataFrame, country: str, from_year: int, to_year: int):
    """Return (last_gdp_in_billions, growth_text) for one country.

    Either value is None/'n/a' when the data point is missing or the growth
    ratio is undefined (missing or zero starting value).
    """
    def value(year):
        s = df.loc[(df['Country Code'] == country) & (df['Year'] == year), 'GDP']
        if s.empty or pd.isna(s.iloc[0]):
            return None
        return s.iloc[0] / 1e9

    first, last = value(from_year), value(to_year)
    if first is None or last is None or first == 0:
        return last, 'n/a'
    return last, f'{last / first:,.2f}x'

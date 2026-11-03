from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gdp_data import filter_gdp, gdp_summary, load_gdp_data, reshape_gdp


@pytest.fixture
def raw():
    return pd.DataFrame({
        'Country Name': ['A land', 'B land'],
        'Country Code': ['AAA', 'BBB'],
        'Indicator Name': ['x', 'x'],
        '2000': [100e9, np.nan],
        '2001': [200e9, 50e9],
        '2002': [np.nan, 0.0],
    })


@pytest.fixture
def df(raw):
    return reshape_gdp(raw)


def test_reshape_long_format(df):
    assert list(df.columns) == ['Country Name', 'Country Code', 'Year', 'GDP']
    assert len(df) == 6
    assert df['Year'].dtype.kind == 'i'
    assert set(df['Year']) == {2000, 2001, 2002}


def test_reshape_without_year_columns_raises():
    with pytest.raises(ValueError):
        reshape_gdp(pd.DataFrame({'Country Name': [], 'Country Code': []}))


def test_filter(df):
    out = filter_gdp(df, ['AAA'], 2001, 2002)
    assert set(out['Country Code']) == {'AAA'}
    assert sorted(out['Year']) == [2001, 2002]
    assert filter_gdp(df, [], 2000, 2002).empty


def test_summary_growth(df):
    assert gdp_summary(df, 'AAA', 2000, 2001) == (200.0, '2.00x')


def test_summary_missing_start(df):
    assert gdp_summary(df, 'BBB', 2000, 2001) == (50.0, 'n/a')


def test_summary_missing_end(df):
    assert gdp_summary(df, 'AAA', 2000, 2002) == (None, 'n/a')


def test_summary_zero_start_no_division_error(df):
    assert gdp_summary(df, 'BBB', 2002, 2001) == (50.0, 'n/a')


def test_summary_unknown_country(df):
    assert gdp_summary(df, 'ZZZ', 2000, 2001) == (None, 'n/a')


def test_real_dataset():
    real = load_gdp_data()
    assert real['Year'].min() == 1960 and real['Year'].max() == 2022
    assert {'DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'} <= set(real['Country Code'])
    last, growth = gdp_summary(real, 'DEU', 1991, 2022)
    assert last > 1000 and growth.endswith('x')
    # Afghanistan has no 2022 value in the data
    assert gdp_summary(real, 'AFG', 1960, 2022)[0] is None


def test_app_runs_and_handles_empty_selection():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(Path(__file__).parent.parent / 'streamlit_app.py'), default_timeout=30).run()
    assert not at.exception
    assert len(at.metric) == 6

    at.multiselect[0].set_value([]).run()
    assert not at.exception
    assert at.warning[0].value == 'Select at least one country'
    assert len(at.metric) == 0

    at.multiselect[0].set_value(['AFG']).run()  # no 2022 data
    assert not at.exception
    assert at.metric[0].value == 'n/a'


def test_country_names_and_billions():
    from gdp_data import country_names, to_billions

    real = load_gdp_data()
    assert country_names(real)['DEU'] == 'Germany'
    assert real['GDP'].notna().all()
    out = to_billions(real.head(3))
    assert (out['GDP (billion USD)'] * 1e9).round().equals(out['GDP'].round())

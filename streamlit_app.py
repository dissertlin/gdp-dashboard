import streamlit as st

from gdp_data import (
    DEFAULT_COUNTRIES, country_names, filter_gdp, gdp_summary, load_gdp_data, to_billions,
)

st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:',
)


@st.cache_data(show_spinner='Loading GDP data...')
def get_gdp_data():
    """Load the GDP CSV once and cache the reshaped result."""
    return load_gdp_data()


@st.cache_data
def get_country_names(df):
    return country_names(df)


gdp_df = get_gdp_data()
names = get_country_names(gdp_df)

st.markdown('''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
''')

min_value = int(gdp_df['Year'].min())
max_value = int(gdp_df['Year'].max())

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=(min_value, max_value))

countries = sorted(names, key=lambda c: names[c])

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    [c for c in DEFAULT_COUNTRIES if c in countries],
    format_func=lambda c: f'{names[c]} ({c})')

if not selected_countries:
    st.warning('Select at least one country')
    st.stop()

filtered_gdp_df = filter_gdp(gdp_df, selected_countries, from_year, to_year)

st.header('GDP over time', divider='gray')

st.line_chart(
    to_billions(filtered_gdp_df),
    x='Year',
    y='GDP (billion USD)',
    color='Country Code',
)

with st.expander('Show data'):
    st.dataframe(
        filtered_gdp_df.sort_values(['Country Code', 'Year']),
        hide_index=True,
        width='stretch',
    )

st.header(f'GDP in {to_year}', divider='gray')

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    last_gdp, growth = gdp_summary(gdp_df, country, from_year, to_year)

    with cols[i % len(cols)]:
        st.metric(
            label=f'{names[country]} ({country})',
            value='n/a' if last_gdp is None else f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color='off' if growth == 'n/a' else 'normal',
        )

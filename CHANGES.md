# Changes

## 1. Bug fixes
- Empty-selection warning checked the list of *all* countries, so it never appeared; now it shows and the page stops.
- A missing end-year GDP rendered as `nanB` / `nanx`; now shows `n/a`.
- Division by zero possible when the start-year GDP was 0; now `n/a`.
- Year range was hard-coded (1960-2022); now detected from the CSV columns.
- Data logic moved into `gdp_data.py` so it can be tested without Streamlit.

## 2. Tests
- `tests/test_gdp_data.py`: reshape, filter, summary edge cases, real dataset, and a Streamlit `AppTest` smoke test (11 tests).
- `requirements-dev.txt` adds pytest.

## 3. Dependencies
- `requirements.txt` was unpinned; now `streamlit>=1.66,<2`, `pandas>=3.0,<4` (verified with streamlit 1.66.1, pandas 3.1.0, Python 3.13; app starts and passes health check).
- Devcontainer image bumped from Python 3.11 (bullseye) to 3.12 (bookworm).

## 4. UI and performance
- Countries shown as "Name (CODE)" and sorted by name; metrics use names too.
- Chart y-axis in billions USD; "Show data" table expander.
- Empty data points dropped and string columns made categorical at load; load is cached with a spinner.
- Replaced deprecated `use_container_width`.

## 5. Documentation
- README: features, screenshots (`docs/`), layout, tests, data update, limitations.

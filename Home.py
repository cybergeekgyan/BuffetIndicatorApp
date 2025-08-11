# streamlit_app.py
"""
Streamlit app to display Buffett Indicator history for top-10 countries (since 1990).
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from main import TOP10_COUNTRIES, fetch_for_countries, combine_countries_to_df

st.set_page_config(page_title="Buffett Indicator Explorer", layout="wide")

st.title("Buffett Indicator Explorer")
st.markdown("""
This app fetches **market capitalization** and **GDP** from the World Bank and computes the Buffett Indicator = *Market Cap / GDP*.
### What is Buffet Indicator?
The **Buffett Indicator** is a stock market valuation metric that compares a country's total stock market capitalization to its gross domestic product (GDP).

**Formula**:
Buffett Indicator (%) = (Total Market Capitalization ÷ GDP) × 100
            
- **Market Capitalization**: Combined value of all publicly traded companies in the country.
- **GDP**: Annual economic output in current prices.

---
""")

# Sidebar controls
st.sidebar.header("Controls")
countries_all = list(TOP10_COUNTRIES.keys())
selected = st.sidebar.multiselect("Select countries (multi-select)", countries_all, default=["United States", "China", "Japan"])

start_year = st.sidebar.number_input("Start year", min_value=1990, max_value= pd.Timestamp.now().year-0, value=1990, step=1)
end_year = st.sidebar.number_input("End year", min_value=1990, max_value=pd.Timestamp.now().year, value=pd.Timestamp.now().year, step=1)
interpolate_method = st.sidebar.selectbox("Missing-year handling", ["Keep gaps (NaN)", "Forward-fill", "Interpolate (linear)"], index=1)

fetch_button = st.sidebar.button("Fetch & Plot")

if fetch_button:
    with st.spinner("Fetching data from World Bank..."):
        try:
            country_data = fetch_for_countries(selected, start_year=int(start_year), end_year=int(end_year))
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            st.stop()
    combined = combine_countries_to_df(country_data)
    if combined.empty:
        st.warning("No data available for the selected countries/years.")
        st.stop()

    # handle missing data
    if interpolate_method == "Forward-fill":
        combined = combined.ffill()
    elif interpolate_method == "Interpolate (linear)":
        combined = combined.interpolate(method="linear")

    # Prepare data for plotting (long)
    df_long = combined.reset_index().melt(id_vars="index", var_name="country", value_name="buffett_percent")
    df_long = df_long.rename(columns={"index": "year"}).dropna(subset=["buffett_percent"])

    # plot
    fig = px.line(df_long, x="year", y="buffett_percent", color="country", markers=True,
                  labels={"buffett_percent": "Buffett Indicator (%)", "year": "Year"},
                  title="Buffett Indicator history (Market Cap / GDP) — %")
    fig.update_layout(autosize=True, legend_title_text="Country")
    st.plotly_chart(fig, use_container_width=True)

    # Latest values table
    latest = combined.loc[combined.index.max()].dropna().sort_values(ascending=False)
    latest_df = pd.DataFrame({"buffett_percent": latest})
    latest_df["buffett_percent_rounded"] = latest_df["buffett_percent"].round(2)
    st.subheader("Latest Buffett Indicator (most recent year available)")
    st.dataframe(latest_df[["buffett_percent_rounded"]].rename(columns={"buffett_percent_rounded":"Buffett (%)"}))

    # allow CSV download
    csv = combined.to_csv(index=True)
    st.download_button("Download CSV (years x countries)", csv, file_name="buffett_indicators.csv", mime="text/csv")

    st.subheader("Raw data (market_cap, gdp, buffett ratio)")
    # Show raw numeric table per-country-year
    # Combine original country_data into a large multi-index table
    raw_tables = []
    for country, df in country_data.items():
        tmp = df.copy()
        tmp = tmp.reset_index().rename(columns={"index":"year"})
        tmp["country"] = country
        raw_tables.append(tmp)
    raw_all = pd.concat(raw_tables, ignore_index=True)
    raw_all = raw_all.sort_values(["country","year"])
    st.dataframe(raw_all)
else:
    st.info("Pick countries and press **Fetch & Plot** to pull World Bank data and display the Buffett Indicator.")

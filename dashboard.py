import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests

st.set_page_config(layout="wide", page_title="🌍 Global Market Dashboard")

# -------------------------------
# Title & Header
# -------------------------------
st.title("🌍 Global Market Live Monitor")
st.markdown("An interactive dashboard showing **GDP**, **S&P 500**, **USD to INR**, **Crude Oil**, and correlations.")
st.markdown("⏱️ _Data auto-refreshes every hour based on free API feeds._")

# -------------------------------
# 1. GDP Data
# -------------------------------
st.header("1️⃣ Top 30 Countries by GDP (2022)")

gdp_url = "http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&date=2022&per_page=300"
try:
    gdp_response = requests.get(gdp_url).json()
    gdp_data = [
        {
            "Country": entry["country"]["value"],
            "iso_alpha": entry["countryiso3code"],
            "GDP": entry["value"]
        }
        for entry in gdp_response[1]
        if entry["value"] and entry["countryiso3code"]
    ]
    gdp_df = pd.DataFrame(gdp_data).sort_values("GDP", ascending=False).head(30)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(gdp_df, x="Country", y="GDP", title="Top 30 GDP Countries", height=400), use_container_width=True)
    with col2:
        gdp_map = px.choropleth(
            gdp_df, locations="iso_alpha", color="GDP",
            hover_name="Country", color_continuous_scale="Plasma",
            title="🌐 GDP Choropleth Map (2022)"
        )
        gdp_map.update_layout(geo=dict(showframe=False, projection_type='natural earth'))
        st.plotly_chart(gdp_map, use_container_width=True)

    st.plotly_chart(px.treemap(gdp_df, path=["Country"], values="GDP", title="🌍 GDP Treemap"), use_container_width=True)
except:
    st.error("Failed to load GDP data.")

# -------------------------------
# 2. S&P 500 Market Data
# -------------------------------
st.header("2️⃣ S&P 500 Market Overview")
try:
    sp500 = yf.Ticker("^GSPC").history(period="1mo")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(px.line(sp500, x=sp500.index, y="Close", title="S&P 500 - Last 30 Days"), use_container_width=True)
    with col4:
        candle = go.Figure(data=[go.Candlestick(
            x=sp500.index,
            open=sp500["Open"],
            high=sp500["High"],
            low=sp500["Low"],
            close=sp500["Close"]
        )])
        candle.update_layout(title="S&P 500 Candlestick")
        st.plotly_chart(candle, use_container_width=True)
except:
    st.error("Failed to load S&P 500 data.")

# -------------------------------
# 3. USD to INR Exchange Rate
# -------------------------------
st.header("3️⃣ USD to INR Exchange Rate")

try:
    fx_response = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=INR", timeout=5)
    fx_data = fx_response.json()
    usd_inr = fx_data["rates"]["INR"] if "rates" in fx_data and "INR" in fx_data["rates"] else "Unavailable"
except:
    usd_inr = "Unavailable"

col5, col6 = st.columns([1, 3])
with col5:
    st.markdown("**Live USD → INR**")
    if isinstance(usd_inr, float):
        st.success(f"1 USD = ₹{usd_inr:.2f}")
    else:
        st.warning("Live rate currently unavailable")

with col6:
    try:
        fx_hist = yf.Ticker("USDINR=X").history(period="1mo")
        if not fx_hist.empty:
            fx_line = px.line(fx_hist, x=fx_hist.index, y="Close", title="USD to INR - Last 30 Days")
            st.plotly_chart(fx_line, use_container_width=True)
        else:
            st.warning("No recent USD/INR history available.")
    except:
        st.error("Unable to fetch USDINR price history.")

# -------------------------------
# 4. Brent Crude Oil Prices
# -------------------------------
st.header("4️⃣ Brent Crude Oil Prices")
try:
    oil = yf.Ticker("BZ=F").history(period="1mo")
    oil_chart = px.line(oil, x=oil.index, y="Close", title="Brent Crude Oil - Last 30 Days")
    st.plotly_chart(oil_chart, use_container_width=True)
except:
    st.error("Error loading Brent Oil data.")

# -------------------------------
# 5. Market Correlation Heatmap
# -------------------------------
st.header("5️⃣ Correlation Heatmap")
try:
    df_corr = pd.DataFrame({
        "S&P 500": sp500["Close"].pct_change(),
        "USD/INR": fx_hist["Close"].pct_change() if 'fx_hist' in locals() else 0,
        "Crude Oil": oil["Close"].pct_change()
    })
    corr = df_corr.corr()
    heatmap = px.imshow(corr, text_auto=True, title="📊 Market Correlation Heatmap")
    st.plotly_chart(heatmap, use_container_width=True)
except:
    st.warning("Unable to render correlation heatmap due to missing data.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("""---""")
st.markdown(
    """
    <div style='text-align: center; font-size: 15px;'>
        <p>🛠️ <strong>Powered by Venkata Saikiran Melam</strong></p>
        <p><em>This dashboard auto-refreshes every hour. Data from World Bank, Yahoo Finance, exchangerate.host</em></p>
    </div>
    """,
    unsafe_allow_html=True
)

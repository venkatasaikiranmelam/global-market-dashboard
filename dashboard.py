import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import requests
from datetime import datetime

st.set_page_config(page_title="Global Market Live Monitor", layout="wide")

st.title("🌐 Global Market Live Monitor")
st.caption("Updated: " + datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'))

# 1️⃣ Global GDP
st.header("1️⃣ Global GDP - Top 30 Countries (2022)")
gdp_url = "http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&date=2022&per_page=300"
try:
    gdp_response = requests.get(gdp_url).json()
    gdp_data = [
        {
            "Country": e["country"]["value"],
            "iso_alpha": e["countryiso3code"],
            "GDP": e["value"]
        }
        for e in gdp_response[1]
        if e["value"] and e["countryiso3code"]
    ]
    gdp_df = pd.DataFrame(gdp_data).sort_values("GDP", ascending=False).head(30)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(gdp_df, x="Country", y="GDP", title="Top 30 GDPs"), use_container_width=True)
    with col2:
        gdp_map = px.choropleth(
            gdp_df, locations="iso_alpha", color="GDP", hover_name="Country",
            color_continuous_scale="Plasma", title="🌍 GDP Choropleth Map"
        )
        gdp_map.update_layout(geo=dict(showframe=False, projection_type='natural earth'))
        st.plotly_chart(gdp_map, use_container_width=True)

    st.plotly_chart(px.treemap(gdp_df, path=["Country"], values="GDP", title="Treemap: Share of GDP"),
                    use_container_width=True)

except:
    st.warning("⚠️ GDP data unavailable.")

# 2️⃣ S&P 500
st.header("2️⃣ S&P 500 - Last 30 Days")
try:
    sp = yf.Ticker("^GSPC").history(period="1mo")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(sp, x=sp.index, y="Close", title="S&P 500 Line Chart"), use_container_width=True)
    with col2:
        candle = go.Figure(data=[go.Candlestick(x=sp.index, open=sp["Open"], high=sp["High"],
                                                low=sp["Low"], close=sp["Close"])])
        candle.update_layout(title="S&P 500 Candlestick")
        st.plotly_chart(candle, use_container_width=True)
except:
    st.warning("⚠️ S&P 500 data unavailable.")

# 3️⃣ USD to INR
st.header("3️⃣ USD to INR Exchange Rate")
try:
    fx_hist = yf.Ticker("USDINR=X").history(period="1mo")
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            live_rate = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=INR").json()
            usd_inr = live_rate["rates"]["INR"]
            st.metric("Live USD → INR", f"{usd_inr:.2f}")
        except:
            st.metric("Live USD → INR", "Unavailable")
    with col2:
        st.plotly_chart(px.line(fx_hist, x=fx_hist.index, y="Close", title="USD to INR - Last 30 Days"),
                        use_container_width=True)
except:
    st.warning("⚠️ USD/INR data unavailable.")

# 4️⃣ Brent Crude Oil
st.header("4️⃣ Brent Crude Oil - Last 30 Days")
try:
    oil = yf.Ticker("BZ=F").history(period="1mo")
    st.plotly_chart(px.line(oil, x=oil.index, y="Close", title="Brent Crude Oil Prices"), use_container_width=True)
except:
    st.warning("⚠️ Crude oil data unavailable.")

# 5️⃣ Market Correlation
st.header("5️⃣ Correlation Between Markets")
try:
    df_corr = pd.DataFrame({
        "S&P 500": sp["Close"].pct_change(),
        "USD/INR": fx_hist["Close"].pct_change(),
        "Crude Oil": oil["Close"].pct_change()
    })
    st.plotly_chart(px.imshow(df_corr.corr(), text_auto=True, title="📊 Correlation Heatmap"), use_container_width=True)
except:
    st.warning("⚠️ Correlation data unavailable.")

# 📌 Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>"
    "<h4>🛠️ Powered by Venkata Saikiran Melam</h4>"
    "<p style='color:gray;'>📌 This dashboard updates hourly. For informational purposes only.</p>"
    "</div>",
    unsafe_allow_html=True
)

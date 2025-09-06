import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="📊 Stock Dashboard (Candlestick)", layout="wide")

# ---------- POPULAR COMPANIES ----------
POPULAR_COMPANIES = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
    "Google (GOOGL)": "GOOGL",
    "Meta (META)": "META",
    "NVIDIA (NVDA)": "NVDA",
    "Netflix (NFLX)": "NFLX",
}

# ---------- UI ----------
st.title("📊 Stock Market Dashboard (Candlestick + Volume)")
st.markdown("Track **candlestick charts, moving averages, and volume** with `mplfinance`.")

with st.sidebar:
    st.header("🔍 Search Settings")
    company = st.selectbox("Select Company", list(POPULAR_COMPANIES.keys()))
    ticker = POPULAR_COMPANIES[company]

    time_period = st.selectbox(
        "Time Period",
        ["5d", "1mo", "3mo", "6mo", "1y"],
        index=1
    )

# ---------- FETCH DATA ----------
df = yf.download(ticker, period=time_period, interval="1d")

if not df.empty:
    # Reset index is NOT needed for mplfinance → it needs DatetimeIndex
    # Add moving averages (50, 200)
    addplots = [
        mpf.make_addplot(df["Close"].rolling(50).mean(), color="blue"),
        mpf.make_addplot(df["Close"].rolling(200).mean(), color="orange"),
    ]

    # Create candlestick chart
    fig, axlist = mpf.plot(
        df,
        type="candle",
        style="yahoo",
        volume=True,
        addplot=addplots,
        figsize=(12, 8),
        returnfig=True
    )

    st.pyplot(fig)

    # ---------- DATA TABLE ----------
    st.subheader("📅 Latest Stock Data")
    st.dataframe(df.tail(), use_container_width=True)

else:
    st.error("No data available for this ticker/period.")

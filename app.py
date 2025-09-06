import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="📊 Advanced Stock Dashboard", layout="wide")

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
st.title("📊 Advanced Stock Market Dashboard")
st.markdown("Track **stock prices, candlesticks, volume, and moving averages** in one dashboard.")

with st.sidebar:
    st.header("🔍 Search Settings")
    company = st.selectbox("Select Company", list(POPULAR_COMPANIES.keys()))
    ticker = POPULAR_COMPANIES[company]

    time_period = st.selectbox(
        "Time Period",
        ["5d", "1mo", "3mo", "6mo", "1y", "5y"],
        index=1
    )

# ---------- FETCH DATA ----------
df = yf.download(ticker, period=time_period, interval="1d")

if not df.empty:
    df = df.reset_index()

    # ---------- MOVING AVERAGES ----------
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    # ---------- CANDLESTICK CHART ----------
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["Date"],
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name="Candlestick"
    ))

    # Moving Averages
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA50"],
        mode="lines", name="MA50",
        line=dict(color="blue", width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA200"],
        mode="lines", name="MA200",
        line=dict(color="orange", width=1.5)
    ))

    fig.update_layout(
        title=f"{ticker} Stock Price ({time_period})",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        height=600
    )

    # ---------- VOLUME BAR CHART ----------
    vol_fig = go.Figure()
    vol_fig.add_trace(go.Bar(
        x=df["Date"], y=df["Volume"],
        name="Volume", marker_color="purple"
    ))
    vol_fig.update_layout(
        title="Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        height=300
    )

    # ---------- DISPLAY ----------
    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(vol_fig, use_container_width=True)

    st.subheader("📅 Latest Stock Data")
    st.dataframe(df.tail(), use_container_width=True)

else:
    st.error("No data available for this ticker/period.")

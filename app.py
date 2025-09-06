import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="📊 Stock Dashboard (Matplotlib)", layout="wide")

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
st.title("📊 Stock Market Dashboard (Matplotlib + Seaborn)")
st.markdown("Track **closing prices, moving averages, and volume** using Matplotlib/Seaborn.")

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

    # ---------- PRICE & MOVING AVERAGES ----------
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["Date"], df["Close"], label="Close Price", color="blue")
    ax.plot(df["Date"], df["MA50"], label="MA50", color="orange", linestyle="--")
    ax.plot(df["Date"], df["MA200"], label="MA200", color="green", linestyle="--")
    ax.set_title(f"{ticker} Closing Price & Moving Averages")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    st.pyplot(fig)

    # ---------- VOLUME CHART ----------
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    sns.barplot(x=df["Date"], y=df["Volume"], ax=ax2, color="purple")
    ax2.set_title(f"{ticker} Trading Volume")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Volume")
    # Rotate x labels for readability
    for label in ax2.get_xticklabels():
        label.set_rotation(45)
    st.pyplot(fig2)

    # ---------- DATA TABLE ----------
    st.subheader("📅 Latest Stock Data")
    st.dataframe(df.tail(), use_container_width=True)

else:
    st.error("No data available for this ticker/period.")

# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="📈 Real-Time Stock Dashboard",
    layout="wide"
)

st.title("📊 Real-Time Stock Market Dashboard")
st.markdown("Track candlesticks, moving averages, volume, and RSI in real time.")

# ---------- USER INPUT ----------
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, AMZN)", "AAPL").upper()
time_period = st.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=2)

# ---------- DATA FETCH ----------
df = yf.download(ticker, period=time_period, interval="1d")

if not df.empty:
    try:
        # Clean data
        df = df.dropna()
        df = df.astype(float)

        # ---------- RSI CALCULATION ----------
        delta = df["Close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        window = 14
        avg_gain = pd.Series(gain).rolling(window=window).mean()
        avg_loss = pd.Series(loss).rolling(window=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        df["RSI"] = rsi

        # ---------- MOVING AVERAGES ----------
        addplots = [
            mpf.make_addplot(df["Close"].rolling(50).mean(), color="blue", width=1),
            mpf.make_addplot(df["Close"].rolling(200).mean(), color="orange", width=1),
            mpf.make_addplot(df["RSI"], panel=1, color="purple", ylabel="RSI")
        ]

        # ---------- PLOT ----------
        fig, axlist = mpf.plot(
            df,
            type="candle",
            style="yahoo",
            volume=True,
            addplot=addplots,
            figsize=(12, 8),
            returnfig=True,
            panel_ratios=(3,1)  # 3:1 ratio for candlesticks vs RSI
        )

        st.pyplot(fig)

        # ---------- DATA TABLE ----------
        st.subheader("📅 Latest Stock Data")
        st.dataframe(df.tail(), use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Could not render chart due to: {e}")

else:
    st.error("❌ No data available for this ticker/period.")

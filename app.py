# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf

# -------- STREAMLIT PAGE CONFIG --------
st.set_page_config(
    page_title="📊 Real-Time Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Real-Time Stock Market Dashboard")
st.markdown("Track candlesticks, moving averages, volume, and RSI in real time.")

# -------- SIDEBAR INPUT --------
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, AMZN)", "TSLA").upper()
time_period = st.selectbox("Select Time Period", ["5d", "1mo", "3mo", "6mo", "1y", "5y"], index=2)

# -------- FETCH STOCK DATA --------
if ticker:
    df = yf.download(ticker, period=time_period, interval="1d", auto_adjust=True)

    if not df.empty:
        try:
            df = df.dropna()

            # ---------- RSI CALCULATION ----------
            delta = df["Close"].diff()
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)

            window = 14
            avg_gain = pd.Series(gain).rolling(window=window).mean()
            avg_loss = pd.Series(loss).rolling(window=window).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            df["RSI"] = rsi.values.flatten()  # ✅ ensure 1D

            # ---------- ADD MOVING AVERAGES + RSI ----------
            addplots = [
                mpf.make_addplot(df["Close"].rolling(50).mean(), color="blue", width=1),
                mpf.make_addplot(df["Close"].rolling(200).mean(), color="orange", width=1),
                mpf.make_addplot(df["RSI"], panel=1, color="purple", ylabel="RSI")
            ]

            # ---------- CANDLESTICK CHART ----------
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

            # ---------- SHOW DATA ----------
            st.subheader("📅 Latest Stock Data")
            st.dataframe(df.tail(), use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Could not render chart due to: {e}")

    else:
        st.error("❌ No data available for this ticker/period.")
else:
    st.info("ℹ️ Enter a ticker symbol to get started.")

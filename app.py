    import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 Real-Time Stock Market Dashboard", page_icon="📈", layout="wide")
st.title("📊 Real-Time Stock Market Dashboard")
st.markdown("Track candlesticks, moving averages, volume, and RSI in real time.")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, AMZN)", "TSLA").upper()
time_period = st.selectbox("Select Time Period", ["5d", "1mo", "3mo", "6mo", "1y", "5y"], index=2)

if ticker:
    df = yf.download(ticker, period=time_period, interval="1d", auto_adjust=True)
    if not df.empty:
        df = df.dropna().copy()

        # ----- Wilder RSI -----
        window = 14
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Wilder's smoothing via EWM with com=window-1 equals:
        # avg_t = (avg_{t-1}*(window-1) + current)/window  [Wilder]
        avg_gain = gain.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
        avg_loss = loss.ewm(alpha=1/window, adjust=False, min_periods=window).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        # If avg_loss was exactly zero, RSI should be 100; if avg_gain was zero and loss>0, RSI should be 0
        rsi = rsi.fillna(np.where((avg_loss == 0) & (avg_gain > 0), 100, np.nan))
        df["RSI"] = rsi

        # ----- Plot with mplfinance -----
        # Build RSI lower panel
        apds = [
            mpf.make_addplot(df["RSI"], panel=1, color="purple", ylabel="RSI(14)"),
            mpf.make_addplot(pd.Series(70, index=df.index), panel=1, color="red", linestyle="--"),
            mpf.make_addplot(pd.Series(30, index=df.index), panel=1, color="green", linestyle="--"),
        ]

        # Create mpf figure and plot; use style and MAs on main panel
        fig = mpf.figure(style="yahoo", figsize=(12, 8))
        ax_main = fig.add_subplot(2, 1, 1)
        ax_rsi = fig.add_subplot(2, 1, 2, sharex=ax_main)

        mpf.plot(
            df,
            type="candle",
            mav=(20, 50),
            volume=True,
            addplot=apds,
            ax=ax_main,
            volume_panel=2,  # mpf will create internal axes; we’re predefining main/RSI
            panel_ratios=(3, 1),
            warn_too_much_data=10000,
            show_nontrading=False,
        )

        st.pyplot(fig)
    else:
        st.warning("No data returned for the selected ticker/period.")

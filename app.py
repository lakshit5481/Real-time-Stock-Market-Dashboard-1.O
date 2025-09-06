import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

st.set_page_config(page_title="📊 Real-Time Stock Market Dashboard", page_icon="📈", layout="wide")
st.title("📊 Real-Time Stock Market Dashboard")
st.markdown("Track candlesticks, moving averages, volume, and RSI in real time.")

# ---------------- Utils ----------------
@st.cache_data(show_spinner=False, ttl=300)
def load_data(ticker: str, period: str, interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
    if not df.empty:
        df = df.dropna().copy()
    return df

def compute_rsi_wilder(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder smoothing via EWM; min_periods enforces initial warmup window
    avg_gain = gain.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # Handle edge cases without fillna(array)
    cond_up = (avg_loss == 0) & (avg_gain > 0)
    cond_down = (avg_gain == 0) & (avg_loss > 0)
    rsi = rsi.mask(cond_up, 100.0).mask(cond_down, 0.0)

    return rsi

# ---------------- UI ----------------
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    ticker = st.text_input("Enter Stock Ticker", "TSLA").upper()
with col2:
    time_period = st.selectbox("Select Time Period", ["5d", "1mo", "3mo", "6mo", "1y", "5y"], index=2)
with col3:
    rsi_window = st.number_input("RSI Window", min_value=5, max_value=50, value=14, step=1)

if ticker:
    df = load_data(ticker, time_period, interval="1d")
    if df.empty:
        st.warning("No data returned for the selected ticker/period.")
    else:
        # Indicators
        if len(df) < rsi_window + 1:
            st.info(f"Not enough data to compute RSI({rsi_window}). Need at least {rsi_window+1} rows, got {len(df)}.")
            df["RSI"] = np.nan
        else:
            df["RSI"] = compute_rsi_wilder(df["Close"], window=rsi_window)

        # Build additional plots (RSI + guides)
        apds = []
        if "RSI" in df:
            apds.extend([
                mpf.make_addplot(df["RSI"], panel=1, color="purple", ylabel=f"RSI({rsi_window})"),
                mpf.make_addplot(pd.Series(70, index=df.index), panel=1, color="red", linestyle="--"),
                mpf.make_addplot(pd.Series(30, index=df.index), panel=1, color="green", linestyle="--"),
            ])

        # Create and render plot
        fig = mpf.figure(style="yahoo", figsize=(13, 8))
        ax_main = fig.add_subplot(2, 1, 1)
        ax_rsi = fig.add_subplot(2, 1, 2, sharex=ax_main)

        mpf.plot(
            df,
            type="candle",
            mav=(20, 50),
            volume=True,
            addplot=apds,
            ax=ax_main,
            panel_ratios=(3, 1),
            warn_too_much_data=10000,
            show_nontrading=False,
        )

        st.pyplot(fig, clear_figure=True)

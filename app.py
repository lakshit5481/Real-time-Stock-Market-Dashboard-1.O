import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="📊 Simple Stock Dashboard", layout="wide")

# ---------- UI ----------
st.title("📊 Simple Stock Dashboard")
st.markdown("Track stock prices and volume in a simple way!")

# Sidebar
st.sidebar.header("🔍 Settings")
ticker = st.sidebar.text_input("Enter Stock Symbol", "AAPL")  # Default Apple
time_period = st.sidebar.selectbox("Select Time Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)

# ---------- FETCH DATA ----------
if ticker:
    st.write(f"### 📌 {ticker} — Period: {time_period}")
    try:
        df = yf.download(ticker, period=time_period, interval="1d", auto_adjust=True)
        df = df.reset_index()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        df = pd.DataFrame()

    # ---------- DISPLAY DATA ----------
    if not df.empty:
        # Price chart
        price_chart = alt.Chart(df).mark_line().encode(
            x="Date:T",
            y="Close:Q",
            tooltip=["Date:T", "Close:Q"]
        ).properties(title="Closing Price", height=300)

        # Volume chart
        volume_chart = alt.Chart(df).mark_bar().encode(
            x="Date:T",
            y="Volume:Q",
            tooltip=["Date:T", "Volume:Q"]
        ).properties(title="Volume", height=300)

        col1, col2 = st.columns(2)
        col1.altair_chart(price_chart, use_container_width=True)
        col2.altair_chart(volume_chart, use_container_width=True)

        st.dataframe(df.tail())  # Show last 5 rows
    else:
        st.error("No data found for this ticker.")

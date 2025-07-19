import yfinance as yf
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Unusual Stock Activity Scanner", layout="centered")
st.title("📈 Unusual Stock Activity Scanner")

# Input stock list
stock_input = st.text_input("Enter tickers (comma-separated):", "TSLA, AAPL, NVDA, GEO, AXP, MARA, SOFI")
watchlist = [x.strip().upper() for x in stock_input.split(",")]

# Threshold sliders
volume_threshold = st.slider("Volume Spike Threshold (x times avg)", 1.0, 10.0, 3.0, 0.5)
price_change_threshold = st.slider("Price Move Threshold (%)", 0.0, 10.0, 4.0, 0.5)

@st.cache_data
def detect_unusual_activity(tickers, volume_factor, price_threshold):
    results = []

    for symbol in tickers:
        data = yf.Ticker(symbol).history(period="7d")
        if len(data) < 2:
            continue

        avg_volume = data['Volume'][:-1].mean()
        today_volume = data['Volume'][-1]
        price_change = ((data['Close'][-1] - data['Open'][-1]) / data['Open'][-1]) * 100

        unusual_volume = today_volume > avg_volume * volume_factor
        large_price_move = abs(price_change) > price_threshold

        if unusual_volume or large_price_move:
            results.append({
                'Ticker': symbol,
                'Price Change %': round(price_change, 2),
                'Volume Today': int(today_volume),
                'Avg Volume (6d)': int(avg_volume),
                'Volume Spike': round(today_volume / avg_volume, 2)
            })

    return pd.DataFrame(results)

if st.button("🔍 Scan Now"):
    df = detect_unusual_activity(watchlist, volume_threshold, price_change_threshold)
    if not df.empty:
        st.success("Unusual activity detected!")
        st.dataframe(df)
    else:
        st.info("No unusual activity found. Try adjusting your settings.")

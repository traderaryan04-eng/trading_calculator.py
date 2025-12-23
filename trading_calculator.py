import streamlit as st
import yfinance as yf
import pandas as pd

# 1. UI Setup
st.set_page_config(page_title="Begusarai Hunter Trader", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🏹 HUNTER TRADING CALCULATOR")
st.caption("Pure Math Version - Back to Basics (Bug Free)")

# 2. Market Inputs
with st.sidebar:
    st.header("📊 Market")
    symbol = st.text_input("Symbol (e.g. BTC-USD, RELIANCE.NS)", value="BTC-USD").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])

# Live Data
try:
    stock = yf.Ticker(symbol)
    current_price = stock.history(period="1d")['Close'].iloc[-1]
    currency = "₹" if ".NS" in symbol else "$"
    st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")
except:
    st.error("Bhai, symbol check karo!")
    st.stop()

# 3. Position Inputs (Kal wala logic)
col1, col2 = st.columns(2)
with col1:
    margin = st.number_input(f"Your Margin ({currency})", value=100.0)
    leverage = st.number_input("Leverage (x)", value=50.0)
with col2:
    entry = st.number_input("Entry Price", value=float(current_price))
    tp_price = st.number_input("Target Price (TP)", value=float(current_price * 1.02))
    sl_price = st.number_input("Stop Loss Price (SL)", value=float(current_price * 0.98))

# 4. Mathematically Correct Logic (v5.0)
# Qty = (Margin * Leverage) / Entry
qty = (margin * leverage) / entry

# PnL = (Price Diff) * Qty
price_diff_live = (current_price - entry) if side == "BUY" else (entry - current_price)
pnl_live = price_diff_live * qty
roe = (pnl_live / margin) * 100

# TP/SL PnL
pnl_tp = (abs(tp_price - entry) * qty)
pnl_sl = (abs(entry - sl_price) * qty)
rr_ratio = pnl_tp / pnl_sl if pnl_sl != 0 else 0

# 5. Dashboard
st.markdown("---")
st.subheader("📋 Trading Dashboard")

status = "✅ PROFIT" if pnl_live > 0 else "❌ LOSS" if pnl_live < 0 else "⏳ NEUTRAL"

# Data table without index
df = pd.DataFrame({
    "Metrics": ["Required Margin", "Quantity", "Live PnL", "ROE %", "TP Profit", "SL Loss", "R:R Ratio"],
    "Value": [
        f"{currency}{margin:,.2f}",
        f"{qty:.4f}",
        f"{currency}{pnl_live:,.2f}",
        f"{roe:.2f}%",
        f"{currency}{pnl_tp:,.2f}",
        f"{currency}{pnl_sl:,.2f}",
        f"1 : {rr_ratio:.2f}"
    ]
})
st.table(df.set_index("Metrics"))

if pnl_live > 0:
    st.balloons()

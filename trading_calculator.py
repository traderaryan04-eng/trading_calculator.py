import streamlit as st
import yfinance as yf
import pandas as pd

# UI Setup
st.set_page_config(page_title="Begusarai Hunter Trader", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🚀 BEGUSARAI HUNTER: TRADER TERMINAL")
st.caption("Position Sizer + Live PnL + Risk Management")

# 1. Sidebar for Inputs
st.sidebar.header("📊 Trade Configuration")
symbol = st.sidebar.text_input("Symbol (BTC-USD / RELIANCE.NS)", value="BTC-USD").upper()
side = st.sidebar.selectbox("Side", ["BUY", "SELL"])

# Auto-detect Market & Currency
currency = "₹" if ".NS" in symbol else "$"
max_lev = 20 if ".NS" in symbol else 200

# 2. Live Data Fetch
try:
    stock = yf.Ticker(symbol)
    current_price = stock.history(period="1d")['Close'].iloc[-1]
    st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")
except:
    st.error("Bhai, symbol sahi daalo!")
    st.stop()

# 3. Entry & Leverage Inputs
col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("Quantity", min_value=0.01, value=1.0)
    leverage = st.slider("Manual Leverage", 1, max_lev, 50)
with col2:
    entry = st.number_input("Entry Price", value=float(current_price))
    tp = st.number_input("Target Profit (TP)", value=float(current_price * 1.02))
    sl = st.number_input("Stop Loss (SL)", value=float(current_price * 0.98))

# 4. Math Logic (Delta/Binance Style)
margin_req = (entry * qty) / leverage
price_diff = (current_price - entry) if side == "BUY" else (entry - current_price)
pnl_live = price_diff * qty * leverage
roe = (pnl_live / margin_req) * 100 if margin_req > 0 else 0

pnl_tp = abs(tp - entry) * qty * leverage
pnl_sl = abs(entry - sl) * qty * leverage

# 5. Dashboard Output
st.markdown("---")
st.subheader("📈 Trading Dashboard")

# Status Logic Fix
if pnl_live > 0:
    status = "✅ PROFIT"
elif pnl_live < 0:
    status = "❌ LOSS"
else:
    status = "⏳ NEUTRAL/ACTIVE"

data = {
    "Field": ["Margin Required", "Live PnL", "ROE %", "Target Profit", "Stop Loss", "Status"],
    "Value": [
        f"{currency}{margin_req:,.2f}",
        f"{currency}{pnl_live:,.2f}",
        f"{roe:.2f}%",
        f"{currency}{pnl_tp:,.2f}",
        f"{currency}{pnl_sl:,.2f}",
        status
    ]
}
st.table(pd.DataFrame(data))

st.info(f"Hunter Tip: {symbol} is a {'Stock' if '.NS' in symbol else 'Crypto/US Asset'}. Max Leverage: {max_lev}x")

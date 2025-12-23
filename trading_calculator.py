import streamlit as st
import yfinance as yf
import pandas as pd

# UI Config
st.set_page_config(page_title="Hunter Pro Terminal", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🏹 HUNTER PRO: ULTIMATE TRADING TERMINAL")
st.caption("Begusarai Edition - Mathematically Perfect & Pro UI")

# 1. Inputs - Market Selection
with st.sidebar:
    st.header("⚙️ Settings")
    symbol = st.text_input("Symbol (BTC-USD / RELIANCE.NS)", value="BTC-USD").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])
    rr_ratio = st.slider("Risk : Reward Ratio (1:X)", 1.0, 5.0, 2.0, 0.5)

# 2. Live Data Fetching
try:
    stock = yf.Ticker(symbol)
    current_price = stock.history(period="1d")['Close'].iloc[-1]
    currency = "₹" if ".NS" in symbol else "$"
    st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")
except:
    st.error("Bhai, symbol invalid hai! Check karke sahi daalo.")
    st.stop()

# 3. Position Configuration
col1, col2, col3 = st.columns(3)
with col1:
    margin_input = st.number_input(f"Your Margin ({currency})", min_value=1.0, value=100.0)
    leverage = st.number_input("Leverage (x)", min_value=1.0, max_value=200.0, value=50.0)

# Real Exchange Math
position_size = margin_input * leverage
qty = position_size / current_price

with col2:
    entry = st.number_input("Entry Price", value=float(current_price))
    # Auto TP/SL Calculation based on R:R
    # Risking 2% of position by default for calculation
    risk_per_share = (entry * 0.02) 
    sl_calc = (entry - risk_per_share) if side == "BUY" else (entry + risk_per_share)
    tp_calc = entry + (abs(entry - sl_calc) * rr_ratio) if side == "BUY" else entry - (abs(entry - sl_calc) * rr_ratio)
    
    tp = st.number_input("Target Profit (TP)", value=float(tp_calc))
    sl = st.number_input("Stop Loss (SL)", value=float(sl_calc))

# 4. Result Calculations (FIXED MATH)
price_diff = (current_price - entry) if side == "BUY" else (entry - current_price)
pnl_live = price_diff * qty
roe = (pnl_live / margin_input) * 100

pnl_tp = abs(tp - entry) * qty
pnl_sl = abs(entry - sl) * qty

# 5. Pro Dashboard UI
st.markdown("---")
st.subheader("📊 Live Trading Dashboard")

status = "✅ PROFIT" if pnl_live > 0 else "❌ LOSS" if pnl_live < 0 else "⏳ ACTIVE"

df_data = {
    "Metrics": ["Required Margin", "Position Size", "Quantity", "Live PnL", "ROE %", "TP Profit", "SL Loss", "Status"],
    "Value": [
        f"{currency}{margin_input:,.2f}",
        f"{currency}{position_size:,.2f}",
        f"{qty:.4f}",
        f"{currency}{pnl_live:,.2f}",
        f"{roe:.2f}%",
        f"{currency}{pnl_tp:,.2f}",
        f"{currency}{pnl_sl:,.2f}",
        status
    ]
}

# Style the table
df = pd.DataFrame(df_data)
st.table(df.set_index('Metrics'))

st.success(f"Hunter Strategy: Risking {currency}{pnl_sl:,.2f} to earn {currency}{pnl_tp:,.2f} (R:R 1:{rr_ratio})")

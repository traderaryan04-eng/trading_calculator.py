import streamlit as st
import yfinance as yf
import pandas as pd

# UI Config
st.set_page_config(page_title="Begusarai Hunter Terminal", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🏹 HUNTER PRO TERMINAL")
st.caption("No Margin Input | Auto Symbol Detection | Blank Slate")

# 1. Market Input (Smart Detection)
with st.sidebar:
    st.header("🔍 Market")
    raw_symbol = st.text_input("Enter Stock/Crypto Name (e.g. RELIANCE, BTC)", value="").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])

# Logic for Auto-Correction
symbol = ""
if raw_symbol:
    if raw_symbol in ["BTC", "ETH", "SOL", "DOGE"]:
        symbol = f"{raw_symbol}-USD"
    elif len(raw_symbol) > 0 and "." not in raw_symbol:
        symbol = f"{raw_symbol}.NS"
    else:
        symbol = raw_symbol

# 2. Live Data Fetch (Sirf tab jab symbol ho)
current_price = 0.0
currency = "$"
if symbol:
    try:
        stock = yf.Ticker(symbol)
        current_price = stock.history(period="1d")['Close'].iloc[-1]
        currency = "₹" if ".NS" in symbol else "$"
        st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")
    except:
        st.warning("Bhai, symbol detect nahi ho raha. Pura naam try karo (e.g. TATAMOTORS)")

# 3. Inputs - Ekdum Khali (0.00)
col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("Quantity", value=0.0, step=0.01)
    leverage = st.number_input("Leverage (x)", value=1.0, step=1.0)
with col2:
    entry = st.number_input("Entry Price", value=0.0)
    tp = st.number_input("Target Price (TP)", value=0.0)
    sl = st.number_input("Stop Loss Price (SL)", value=0.0)

# 4. Calculation Logic (Sirf tab jab data ho)
if qty > 0 and entry > 0:
    # Math: Margin = (Entry * Qty) / Leverage
    req_margin = (entry * qty) / leverage
    pnl_live = ((current_price - entry) if side == "BUY" else (entry - current_price)) * qty * leverage
    roe = (pnl_live / req_margin) * 100 if req_margin > 0 else 0
    
    pnl_tp = abs(tp - entry) * qty * leverage
    pnl_sl = abs(entry - sl) * qty * leverage
    rr = pnl_tp / pnl_sl if pnl_sl > 0 else 0

    # 5. Dashboard
    st.markdown("---")
    st.subheader("📋 Trading Dashboard")
    
    df = pd.DataFrame({
        "Metrics": ["Required Margin", "Live PnL", "ROE %", "TP Profit", "SL Loss", "R:R Ratio"],
        "Value": [
            f"{currency}{req_margin:,.2f}",
            f"{currency}{pnl_live:,.2f}",
            f"{roe:.2f}%",
            f"{currency}{pnl_tp:,.2f}",
            f"{currency}{pnl_sl:,.2f}",
            f"1 : {rr:.2f}"
        ]
    })
    st.table(df.set_index("Metrics"))
    
    if pnl_live > 0: st.success("✅ PROFIT")
    elif pnl_live < 0: st.error("❌ LOSS")
else:
    st.info("Bhai, Quantity aur Entry Price daalo calculation dekhne ke liye.")

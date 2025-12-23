import streamlit as st
import yfinance as yf
import pandas as pd

# UI Setup
st.set_page_config(page_title="Begusarai Hunter Terminal", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🏹 HUNTER PRO TERMINAL")
st.caption("Smart Detection | Zero Confusion | Blank Slate")

# 1. Market Input
with st.sidebar:
    st.header("🔍 Market")
    user_input = st.text_input("Enter Name (e.g. TATAMOTORS, BTC)", value="").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])

# --- SMART DETECTION LOGIC ---
symbol = ""
current_price = 0.0
currency = "$"

if user_input:
    # List of options to try in order
    options = [f"{user_input}.NS", f"{user_input}-USD", user_input]
    
    for opt in options:
        try:
            ticker = yf.Ticker(opt)
            hist = ticker.history(period="1d")
            if not hist.empty:
                symbol = opt
                current_price = hist['Close'].iloc[-1]
                currency = "₹" if ".NS" in opt else "$"
                break
        except:
            continue

# 2. Display Price
if symbol:
    st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")
elif user_input:
    st.error(f"Bhai, '{user_input}' nahi mil raha. Ek baar spelling check kar lo.")

# 3. Inputs (Blank Slate)
col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("Quantity", value=0.0, step=0.01, format="%.2f")
    leverage = st.number_input("Leverage (x)", value=1.0, step=1.0)
with col2:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    tp = st.number_input("Target Price (TP)", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss Price (SL)", value=0.0, format="%.2f")

# 4. Calculation Logic
if qty > 0 and entry > 0 and current_price > 0:
    req_margin = (entry * qty) / leverage
    price_diff = (current_price - entry) if side == "BUY" else (entry - current_price)
    pnl_live = price_diff * qty * (1 if leverage == 1 else leverage/leverage) # Fixed for Spot/Future
    # Real PnL logic
    pnl_real = price_diff * qty
    roe = (pnl_real / req_margin) * 100 if req_margin > 0 else 0
    
    pnl_tp = abs(tp - entry) * qty
    pnl_sl = abs(entry - sl) * qty
    rr = pnl_tp / pnl_sl if pnl_sl > 0 else 0

    # 5. Dashboard
    st.markdown("---")
    st.subheader("📋 Trading Dashboard")
    
    df = pd.DataFrame({
        "Metrics": ["Required Margin", "Quantity", "Live PnL", "ROE %", "TP Profit", "SL Loss", "R:R Ratio"],
        "Value": [
            f"{currency}{req_margin:,.2f}",
            f"{qty:.4f}",
            f"{currency}{pnl_real:,.2f}",
            f"{roe:.2f}%",
            f"{currency}{pnl_tp:,.2f}",
            f"{currency}{pnl_sl:,.2f}",
            f"1 : {rr:.2f}"
        ]
    })
    st.table(df.set_index("Metrics"))
    
    if pnl_real > 0: st.success("✅ PROFIT")
    elif pnl_real < 0: st.error("❌ LOSS")
else:
    if user_input:
        st.info("Bhai, Quantity aur Entry Price daalo calculation ke liye.")

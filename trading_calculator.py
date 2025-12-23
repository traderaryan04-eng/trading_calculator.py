import streamlit as st
import yfinance as yf
import pandas as pd

# UI Config
st.set_page_config(page_title="Begusarai Hunter Terminal", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🏹 HUNTER PRO TERMINAL")
st.caption("Auto-Detect Fixed | No Margin Confusion | Blank Slate")

# 1. Market Input
with st.sidebar:
    st.header("🔍 Market")
    user_input = st.text_input("Enter Name (e.g. TATAMOTORS, BTC)", value="").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])

# --- BULLETPROOF DETECTION ---
symbol = ""
current_price = 0.0
currency = "$"

if user_input:
    # 1. Try Indian Stock (.NS)
    try:
        t_ns = yf.Ticker(f"{user_input}.NS")
        price_ns = t_ns.fast_info['lastPrice'] # Fast info use kar rahe
        if price_ns > 0:
            symbol, current_price, currency = f"{user_input}.NS", price_ns, "₹"
    except:
        # 2. Try Crypto (-USD)
        try:
            t_usd = yf.Ticker(f"{user_input}-USD")
            price_usd = t_usd.fast_info['lastPrice']
            if price_usd > 0:
                symbol, current_price, currency = f"{user_input}-USD", price_usd, "$"
        except:
            # 3. Try Plain
            try:
                t_plain = yf.Ticker(user_input)
                price_p = t_plain.fast_info['lastPrice']
                if price_p > 0:
                    symbol, current_price, currency = user_input, price_p, "$"
            except:
                st.error(f"Bhai, '{user_input}' nahi mila. Pura ticker daal ke dekho (e.g. TATAMOTORS.NS)")

# 2. Display Price
if symbol:
    st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")

# 3. Inputs (Ekdum Blank)
col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("Quantity", value=0.0)
    leverage = st.number_input("Leverage (x)", value=1.0)
with col2:
    entry = st.number_input("Entry Price", value=0.0)
    tp = st.number_input("Target Price (TP)", value=0.0)
    sl = st.number_input("Stop Loss Price (SL)", value=0.0)

# 4. Calculation Logic
if qty > 0 and entry > 0 and current_price > 0:
    # Pure Position Math
    position_size = entry * qty
    req_margin = position_size / leverage
    
    # Real Live PnL (Binance Style)
    price_diff = (current_price - entry) if side == "BUY" else (entry - current_price)
    pnl_live = price_diff * qty
    roe = (pnl_live / req_margin) * 100 if req_margin > 0 else 0
    
    pnl_tp = abs(tp - entry) * qty
    pnl_sl = abs(entry - sl) * qty
    rr = pnl_tp / pnl_sl if pnl_sl > 0 else 0

    # 5. Dashboard
    st.markdown("---")
    st.subheader("📋 Trading Dashboard")
    
    df = pd.DataFrame({
        "Metrics": ["Required Margin", "Position Size", "Live PnL", "ROE %", "TP Profit", "SL Loss", "R:R Ratio"],
        "Value": [
            f"{currency}{req_margin:,.2f}",
            f"{currency}{position_size:,.2f}",
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
    if user_input and symbol:
        st.info("Bhai, Quantity aur Entry Price daalo calculation ke liye.")

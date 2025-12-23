import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq

# 1. UI Configuration (Wide & Mobile Friendly)
st.set_page_config(page_title="Hunter AI Terminal", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 2. SECRETS & AI SETUP ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("Bhai, Secrets mein 'GROQ_API_KEY' check karo!")
    GROQ_KEY = None

def get_ai_insight(symbol, price, side, pnl, roe):
    # NEWS + PREDICTION Prompt [web:113]
    prompt = f"""
    You are a Begusarai Trader AI. Analyze this trade:
    Symbol: {symbol} | Price: {price} | Side: {side} | PnL: {pnl} | ROE: {roe}%
    
    Tasks:
    1. Latest generic market news related to this asset.
    2. Short-term Price Prediction (Bullish/Bearish).
    3. Final advice for a 'Hunter' trader.
    Speak in Hinglish (Desi style). Keep it short.
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except:
        return "Bhai, AI ne jawab nahi diya. Check API!"

# --- 3. MAIN UI (No Sidebar for Mobile Ease) ---
st.title("🏹 HUNTER AI TERMINAL v8.5")
st.caption("Mobile Optimized | AI News & Predictions")

# Market Input on Main Screen (Fixes Mobile Visibility) [web:102]
with st.container():
    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        user_input = st.text_input("Stock/Crypto Name (e.g. TATAMOTORS, BTC)", value="").upper().strip()
    with col_in2:
        side = st.selectbox("Trade Side", ["BUY", "SELL"])

symbol, current_price, currency = "", 0.0, "$"

if user_input:
    for suffix in [".NS", "-USD", ""]:
        try:
            t = yf.Ticker(f"{user_input}{suffix}")
            p = t.fast_info['lastPrice']
            if p > 0:
                symbol, current_price = f"{user_input}{suffix}", p
                currency = "₹" if ".NS" in symbol else "$"
                break
        except: continue

# --- 4. BLANK SLATE DASHBOARD ---
if symbol:
    st.info(f"🟢 Live {symbol}: {currency}{current_price:,.2f}")

    # Inputs Grid
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        qty = st.number_input("Quantity", value=0.0)
        leverage = st.number_input("Leverage (x)", value=1.0)
    with col_b:
        entry = st.number_input("Entry Price", value=0.0)
        tp = st.number_input("Target (TP)", value=0.0)
    with col_c:
        sl = st.number_input("Stop Loss (SL)", value=0.0)

    # Calculation Logic
    if qty > 0 and entry > 0:
        pos_size = entry * qty
        req_margin = pos_size / leverage
        pnl_real = ((current_price - entry) if side == "BUY" else (entry - current_price)) * qty
        roe = (pnl_real / req_margin) * 100 if req_margin > 0 else 0
        pnl_tp = abs(tp - entry) * qty
        pnl_sl = abs(entry - sl) * qty
        rr = pnl_tp / pnl_sl if pnl_sl > 0 else 0

        st.markdown("---")
        st.subheader("📋 Dashboard")
        
        # Compact Table for Mobile [web:108]
        df = pd.DataFrame({
            "Metrics": ["Margin", "PnL", "ROE %", "TP/SL Profit", "R:R"],
            "Value": [f"{currency}{req_margin:,.0f}", f"{currency}{pnl_real:,.2f}", f"{roe:.1f}%", f"{pnl_tp:,.0f} / {pnl_sl:,.0f}", f"1:{rr:.1f}"]
        })
        st.table(df.set_index("Metrics"))

        # --- AI NEWS & PREDICTION BUTTON ---
        if st.button("🤖 GET AI NEWS & PREDICTION"):
            with st.expander("Hunter AI Analysis", expanded=True): [web:117]
                with st.spinner("AI analysis kar raha hai..."):
                    res = get_ai_insight(symbol, current_price, side, f"{currency}{pnl_real:,.2f}", round(roe, 2))
                    st.write(res)
else:
    if user_input: st.error("Bhai, symbol dhoondhne mein error hai.")

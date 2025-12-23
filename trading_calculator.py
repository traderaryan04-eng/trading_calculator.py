import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq
import os

# --- 1. SETTINGS & AI SETUP ---
st.set_page_config(page_title="Hunter AI Terminal", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# Groq API Setup
GROQ_KEY = st.secrets.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
client = Groq(api_key=GROQ_KEY)

def get_ai_analysis(symbol, price, side, pnl, roe):
    prompt = f"""
    Bhai, main ek trader hoon. Mera current trade details ye hain:
    Stock/Crypto: {symbol}
    Current Price: {price}
    Side: {side}
    Live PnL: {pnl}
    ROE: {roe}%
    
    Mujhe is stock/coin ke baare mein short analysis do. 
    1. Current trend kya lag raha hai?
    2. Kya mujhe hold karna chahiye ya profit book karna chahiye?
    Ekdum trader wali Hinglish bhasha mein jawab do (short and powerful).
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except:
        return "Bhai, Groq API key check karo ya network issue hai!"

# --- 2. SMART SYMBOL DETECTION ---
with st.sidebar:
    st.header("🔍 Market Search")
    user_input = st.text_input("Enter Name (e.g. RELIANCE, BTC, ETH)", value="").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])

symbol = ""
current_price = 0.0
currency = "$"

if user_input:
    # Logic: Pehle Indian Stock try karo, fir Crypto
    for suffix in [".NS", "-USD", ""]:
        try:
            temp_sym = f"{user_input}{suffix}"
            t = yf.Ticker(temp_sym)
            p = t.fast_info['lastPrice']
            if p > 0:
                symbol, current_price = temp_sym, p
                currency = "₹" if ".NS" in temp_sym else "$"
                break
        except: continue

# --- 3. UI DASHBOARD ---
st.title("🏹 HUNTER AI TERMINAL v8.0")

if symbol:
    st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")
elif user_input:
    st.error("Bhai, ye symbol nahi mil raha. Sahi naam daalo.")

# Blank Slate Inputs (Sab 0.00 se start hoga)
col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("Quantity", value=0.0, step=0.01, format="%.2f")
    leverage = st.number_input("Leverage (x)", value=1.0, step=1.0)
with col2:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    tp = st.number_input("Target Price (TP)", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss Price (SL)", value=0.0, format="%.2f")

# --- 4. CALCULATION & AI BUTTON ---
if qty > 0 and entry > 0:
    # Math Engine
    pos_size = entry * qty
    req_margin = pos_size / leverage
    pnl_real = ((current_price - entry) if side == "BUY" else (entry - current_price)) * qty
    roe = (pnl_real / req_margin) * 100 if req_margin > 0 else 0
    pnl_tp = abs(tp - entry) * qty
    pnl_sl = abs(entry - sl) * qty
    rr = pnl_tp / pnl_sl if pnl_sl > 0 else 0

    st.markdown("---")
    st.subheader("📋 Trading Dashboard")
    
    df = pd.DataFrame({
        "Metrics": ["Required Margin", "Position Size", "Live PnL", "ROE %", "TP Profit", "SL Loss", "R:R Ratio"],
        "Value": [
            f"{currency}{req_margin:,.2f}",
            f"{currency}{pos_size:,.2f}",
            f"{currency}{pnl_real:,.2f}",
            f"{roe:.2f}%",
            f"{currency}{pnl_tp:,.2f}",
            f"{currency}{pnl_sl:,.2f}",
            f"1 : {rr:.2f}"
        ]
    })
    st.table(df.set_index("Metrics"))

    # --- AI ANALYSIS BUTTON ---
    if st.button("🤖 GET AI ANALYSIS"):
        with st.spinner("Hunter AI analysis kar raha hai..."):
            analysis = get_ai_analysis(symbol, current_price, side, f"{currency}{pnl_real:,.2f}", round(roe, 2))
            st.info(analysis)

else:
    if user_input:
        st.info("Bhai, Quantity aur Entry daalo tabhi calculation dikhega.")

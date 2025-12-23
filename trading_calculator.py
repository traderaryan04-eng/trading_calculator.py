import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq

# 1. UI Setup
st.set_page_config(page_title="Begusarai Hunter Terminal", layout="centered")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🏹 HUNTER AI TERMINAL v8.3")
st.caption("Stable AI Model | Smart Detection | Blank Slate")

# --- 2. SECRETS & AI SETUP ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("Bhai, Streamlit Secrets mein 'GROQ_API_KEY' nahi mil raha!")
    GROQ_KEY = None

def get_ai_analysis(symbol, price, side, pnl, roe):
    if not GROQ_KEY: return "API Key missing!"
    
    prompt = f"""
    Bhai, main Begusarai se ek trader hoon. Mera current trade:
    Symbol: {symbol} | Price: {price} | Side: {side}
    Live PnL: {pnl} | ROE: {roe}%
    
    Mujhe short analysis do trader style Hinglish mein:
    1. Trend kaisa hai?
    2. Hold karun ya Exit?
    Short and powerful jawab dena.
    """
    try:
        # Using the most stable model to avoid decommission errors [web:85]
        completion = client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 3. SMART SYMBOL DETECTION ---
with st.sidebar:
    st.header("🔍 Market Search")
    user_input = st.text_input("Enter Name (e.g. RELIANCE, BTC, ETH)", value="").upper().strip()
    side = st.selectbox("Side", ["BUY", "SELL"])

symbol, current_price, currency = "", 0.0, "$"

if user_input:
    # Auto-detect logic (.NS -> -USD -> Plain)
    for suffix in [".NS", "-USD", ""]:
        try:
            t = yf.Ticker(f"{user_input}{suffix}")
            p = t.fast_info['lastPrice']
            if p > 0:
                symbol, current_price = f"{user_input}{suffix}", p
                currency = "₹" if ".NS" in symbol else "$"
                break
        except: continue

# --- 4. BLANK SLATE UI ---
if symbol:
    st.metric(label=f"Live {symbol} Price", value=f"{currency}{current_price:,.2f}")
elif user_input:
    st.error(f"Bhai, '{user_input}' dhoondhne mein dikkat ho rahi hai.")

col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("Quantity", value=0.0, format="%.2f")
    leverage = st.number_input("Leverage (x)", value=1.0, step=1.0)
with col2:
    entry = st.number_input("Entry Price", value=0.0, format="%.2f")
    tp = st.number_input("Target Price (TP)", value=0.0, format="%.2f")
    sl = st.number_input("Stop Loss Price (SL)", value=0.0, format="%.2f")

# --- 5. MATH & DASHBOARD ---
if qty > 0 and entry > 0 and current_price > 0:
    pos_size = entry * qty
    req_margin = pos_size / leverage
    price_diff = (current_price - entry) if side == "BUY" else (entry - current_price)
    pnl_real = price_diff * qty
    roe = (pnl_real / req_margin) * 100 if req_margin > 0 else 0
    pnl_tp = abs(tp - entry) * qty
    pnl_sl = abs(entry - sl) * qty
    rr = pnl_tp / pnl_sl if pnl_sl > 0 else 0

    st.markdown("---")
    st.subheader("📋 Live Trading Dashboard")
    
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
    # Display table without the index (0, 1, 2...)
    st.table(df.set_index("Metrics"))

    if st.button("🤖 GET AI ANALYSIS"):
        with st.spinner("Hunter AI dimaag laga raha hai..."):
            res = get_ai_analysis(symbol, current_price, side, f"{currency}{pnl_real:,.2f}", round(roe, 2))
            st.info(res)
else:
    if user_input and symbol:
        st.info("Bhai, Quantity aur Entry daalo tabhi calculation dikhega.")

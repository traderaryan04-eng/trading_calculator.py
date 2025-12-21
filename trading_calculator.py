import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Hunter Trading Calculator", layout="wide")

st.title("🔥 HUNTER TRADING CALCULATOR v5.0")
st.markdown("---")

# Sidebar
st.sidebar.header("📊 Trade Setup")
symbol = st.sidebar.text_input("Symbol", value="ETH-USD").upper()

# Live price
try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    live_price = data['Close'].iloc[-1]
    st.sidebar.metric("LIVE PRICE", f"${live_price:.2f}")
except:
    live_price = st.sidebar.number_input("Manual Price", value=3000.0)

# Main inputs
col1, col2 = st.columns(2)
with col1:
    qty = st.number_input("Quantity", value=1.0, min_value=0.01, step=0.1)
with col2:
    leverage = st.number_input("Leverage", value=50.0, min_value=1.0, max_value=200.0, step=5.0)

side = st.radio("BUY/SELL", ["BUY", "SELL"])
entry_price = st.number_input("Entry Price", value=live_price)
tp_price = st.number_input("TP Price", value=live_price*1.02)
sl_price = st.number_input("SL Price", value=live_price*0.98)

if st.button("🚀 CALCULATE", type="primary"):
    # Calculations
    position_value = qty * entry_price
    required_margin = position_value / leverage
    
    if side == "BUY":
        pnl_live = (live_price - entry_price) * qty
        pnl_tp = (tp_price - entry_price) * qty
        pnl_sl = (sl_price - entry_price) * qty
    else:
        pnl_live = (entry_price - live_price) * qty
        pnl_tp = (entry_price - tp_price) * qty
        pnl_sl = (entry_price - sl_price) * qty
    
    roe = (pnl_live / required_margin) * 100
    
    # Results
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💳 Required Margin", f"${required_margin:.2f}")
    with col2:
        st.metric("💵 LIVE PnL", f"${pnl_live:.2f}", delta=f"{roe:.1f}%")
    with col3:
        st.metric("📈 ROE", f"{roe:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎯 TP Profit", f"${pnl_tp:.2f}")
        st.metric("🛑 SL Loss", f"${pnl_sl:.2f}")
    with col2:
        st.info(f"""
        **Trade Summary:**
        - 📦 Quantity: {qty:.4f} {symbol}
        - 💰 Position: ${position_value:.2f}
        - ⚡ Leverage: {leverage}x
        """)

st.markdown("---")
st.caption("Made by Hunter 🚀 | Production Ready!")

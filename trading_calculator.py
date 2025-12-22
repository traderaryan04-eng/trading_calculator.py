import streamlit as st
import yfinance as yf
import pandas as pd

# ===== Hide Streamlit default UI (footer, menu, header) =====
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ===== Page config =====
st.set_page_config(
    page_title="Hunter Trading Calculator",
    page_icon="💹",
    layout="centered",
)

st.title("💹 Hunter All-in-One Trading Calculator")
st.write("Position Size + PnL + ROE + TP/SL in one place.")

# ===== Inputs =====
st.subheader("🧮 Trade Inputs")

col1, col2 = st.columns(2)
with col1:
    symbol = st.text_input("Symbol (ETH-USD / BTC-USD / TATAMOTORS.NS)", value="ETH-USD").upper()
    side = st.selectbox("Side", ["BUY", "SELL"])
    leverage = st.number_input("Leverage (1–200x)", min_value=1, max_value=200, value=50)
with col2:
    margin = st.number_input("Capital / Margin (in account currency)", min_value=0.0, value=100.0)
    entry_price = st.number_input("Entry Price", min_value=0.0, value=3000.0)
    qty_manual = st.number_input("Quantity (optional, 0 = auto from margin)", min_value=0.0, value=0.0)

col3, col4 = st.columns(2)
with col3:
    tp_price = st.number_input("Take Profit (TP) Price", min_value=0.0, value=2940.0)
with col4:
    sl_price = st.number_input("Stop Loss (SL) Price", min_value=0.0, value=3020.0)

st.markdown("---")

# ===== Live price fetch =====
st.subheader("💲 Live Market Data")

current_price = None
currency_symbol = "$"

try:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")
    current_price = float(data["Close"].iloc[-1])

    info = ticker.info
    currency = info.get("currency", "USD")
    if currency in ["USD", "USDT"]:
        currency_symbol = "$"
    elif currency == "INR":
        currency_symbol = "₹"
    else:
        currency_symbol = currency + " "
except Exception:
    st.warning("Live price fetch error, using Entry Price as current price.")
    current_price = entry_price

col_lp, col_cp = st.columns(2)
with col_lp:
    st.metric("Live Price", f"{currency_symbol}{current_price:,.2f}")
with col_cp:
    st.metric("Entry Price", f"{currency_symbol}{entry_price:,.2f}")

st.markdown("---")

# ===== Core calculations =====

# Position size from margin & leverage if qty not given
if entry_price > 0:
    if qty_manual > 0:
        qty = qty_manual
        position_value = qty * entry_price
        required_margin = position_value / leverage
    else:
        position_value = margin * leverage
        qty = position_value / entry_price
        required_margin = margin
else:
    qty = 0.0
    position_value = 0.0
    required_margin = 0.0

# PnL function
def calc_pnl(entry, price, quantity, side_):
    if side_ == "BUY":
        return (price - entry) * quantity
    else:
        return (entry - price) * quantity

# Live PnL, TP PnL, SL PnL
pnl_live = calc_pnl(entry_price, current_price, qty, side)
pnl_tp = calc_pnl(entry_price, tp_price, qty, side)
pnl_sl = calc_pnl(entry_price, sl_price, qty, side)

# ROE (return on equity) based on margin
if required_margin > 0:
    roe = (pnl_live / required_margin) * 100
else:
    roe = 0.0

# Risk / Reward (R:R) from SL & TP
risk = abs(pnl_sl)
reward = abs(pnl_tp)
if risk > 0:
    rr = reward / risk
else:
    rr = 0.0

# ===== Output cards =====
st.subheader("📈 Position Overview")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Quantity", f"{qty:,.4f}")
with col_b:
    st.metric("Position Value", f"{currency_symbol}{position_value:,.2f}")
with col_c:
    st.metric("Required Margin", f"{currency_symbol}{required_margin:,.2f}")

st.markdown("---")

st.subheader("💰 PnL & Risk Metrics")

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    st.metric("Live PnL", f"{currency_symbol}{pnl_live:,.2f}")
with col_p2:
    st.metric("TP PnL", f"{currency_symbol}{pnl_tp:,.2f}")
with col_p3:
    st.metric("SL PnL", f"{currency_symbol}{pnl_sl:,.2f}")

col_r1, col_r2 = st.columns(2)
with col_r1:
    st.metric("ROE", f"{roe:,.1f}%")
with col_r2:
    st.metric("Risk / Reward", f"1 : {rr:,.2f}")

st.markdown("---")

# ===== Quick Summary Table =====
st.subheader("📊 Quick Summary Table")

df = pd.DataFrame(
    {
        "Metric": [
            "Required Margin",
            "Position Value",
            "Live PnL",
            "TP PnL",
            "SL PnL",
            "ROE %",
            "Risk/Reward (R:R)",
        ],
        "Value": [
            f"{currency_symbol}{required_margin:,.2f}",
            f"{currency_symbol}{position_value:,.2f}",
            f"{currency_symbol}{pnl_live:,.2f}",
            f"{currency_symbol}{pnl_tp:,.2f}",
            f"{currency_symbol}{pnl_sl:,.2f}",
            f"{roe:,.1f}%",
            f"1 : {rr:.2f}",
        ],
    }
)

st.table(df)

st.caption("Hunter All-in-One Trading Calculator – Position Size + PnL + ROE + TP/SL")

import streamlit as st
import yfinance as yf
import pandas as pd

# ================== HIDE STREAMLIT MENU + FOOTER ==================
hide_default_format = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    footer:before {content: ''; visibility: hidden;}
    </style>
"""
st.markdown(hide_default_format, unsafe_allow_html=True)

# ================== PAGE CONFIG + BASIC THEME ==================
st.set_page_config(
    page_title="Hunter Trading Calculator",
    page_icon="💹",
    layout="centered",
)

page_bg = """
<style>
.stApp {
    background-color: #050509;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown(
    "<h1 style='text-align:center; margin-bottom:0;'>💹 Hunter Trading Calculator</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#cccccc;'>Position Size · PnL · ROE · TP/SL (Crypto & Stocks)</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ================== TRADE INPUTS ==================
st.subheader("🧮 Trade Inputs")

col1, col2 = st.columns(2)
with col1:
    symbol = st.text_input(
        "Symbol (e.g. BTC-USD, ETH-USD, TATAMOTORS.NS)",
        value="BTC-USD"
    ).upper().strip()

    side = st.selectbox("Side", ["BUY", "SELL"])
    leverage = st.number_input(
        "Leverage (1–200x)",
        min_value=1,
        max_value=200,
        value=50,
    )

with col2:
    st.markdown("**Account Margin:** Not required, calculator works with quantity only.")
    entry_price = st.number_input(
        "Entry Price",
        min_value=0.0,
        value=30000.0,
        help="If live price ke aas-paas daal, exact na bhi ho chalega.",
    )

col3, col4 = st.columns(2)
with col3:
    qty = st.number_input(
        "Quantity (Contracts / Coins / Shares)",
        min_value=0.0,
        value=0.10,
    )
with col4:
    tp_price = st.number_input(
        "Take Profit (TP) Price",
        min_value=0.0,
        value=31000.0,
    )

col5, col6 = st.columns(2)
with col5:
    sl_price = st.number_input(
        "Stop Loss (SL) Price",
        min_value=0.0,
        value=29500.0,
    )

st.markdown("---")

# ================== ASSET TYPE DETECTION ==================
asset_type = "Stock"
if "-USD" in symbol or "-USDT" in symbol or "-PERP" in symbol:
    asset_type = "Crypto"
elif symbol.endswith(".NS") or symbol.endswith(".BO"):
    asset_type = "Indian Stock"

st.info(f"Detected: **{asset_type}**")

# ================== LIVE PRICE + CURRENCY ==================
st.subheader("💲 Live Market Data")

current_price = None
currency_symbol = "$"
currency_code = "USD"

if symbol:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            current_price = float(data["Close"].iloc[-1])
        else:
            current_price = entry_price

        info = ticker.info
        currency_code = info.get("currency", "USD") or "USD"  # yfinance currency field [web:32][web:41]

        if currency_code in ["USD", "USDT"]:
            currency_symbol = "$"
        elif currency_code == "INR":
            currency_symbol = "₹"
        elif currency_code == "EUR":
            currency_symbol = "€"
        elif currency_code == "GBP":
            currency_symbol = "£"
        else:
            currency_symbol = f"{currency_code} "

    except Exception:
        st.warning("Live price fetch error, using Entry Price as current price.")
        current_price = entry_price
else:
    current_price = entry_price

if entry_price == 0 and current_price:
    entry_price = current_price

col_lp, col_ep = st.columns(2)
with col_lp:
    st.metric("Live Price", f"{currency_symbol}{current_price:,.2f}")
with col_ep:
    st.metric("Entry Price", f"{currency_symbol}{entry_price:,.2f}")

st.caption(f"Currency detected: {currency_code}")
st.markdown("---")

# ================== CALCULATIONS ==================
def calc_pnl(entry, price, quantity, side_):
    if price == 0 or quantity == 0 or entry == 0:
        return 0.0
    if side_ == "BUY":
        return (price - entry) * quantity
    else:
        return (entry - price) * quantity

position_value = qty * entry_price
required_margin = position_value / leverage if leverage > 0 else position_value

pnl_live = calc_pnl(entry_price, current_price, qty, side)
pnl_tp = calc_pnl(entry_price, tp_price, qty, side) if tp_price > 0 else 0.0
pnl_sl = calc_pnl(entry_price, sl_price, qty, side) if sl_price > 0 else 0.0

if required_margin > 0:
    roe = (pnl_live / required_margin) * 100
else:
    roe = 0.0

risk = abs(pnl_sl)
reward = abs(pnl_tp)
if risk > 0 and reward > 0:
    rr = reward / risk
else:
    rr = 0.0

# ================== POSITION OVERVIEW ==================
st.subheader("📈 Position Overview")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Quantity", f"{qty:,.4f}")
with col_b:
    st.metric("Position Value", f"{currency_symbol}{position_value:,.2f}")
with col_c:
    st.metric("Used Margin (from qty & lev)", f"{currency_symbol}{required_margin:,.2f}")

st.markdown("---")

# ================== PnL & RISK ==================
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

# ================== SUMMARY TABLE ==================
st.subheader("📊 Quick Summary Table")

df = pd.DataFrame(
    {
        "Metric": [
            "Position Value",
            "Used Margin",
            "Live PnL",
            "TP PnL",
            "SL PnL",
            "ROE %",
            "Risk/Reward (R:R)",
        ],
        "Value": [
            f"{currency_symbol}{position_value:,.2f}",
            f"{currency_symbol}{required_margin:,.2f}",
            f"{currency_symbol}{pnl_live:,.2f}",
            f"{currency_symbol}{pnl_tp:,.2f}",
            f"{currency_symbol}{pnl_sl:,.2f}",
            f"{roe:,.1f}%",
            f"1 : {rr:.2f}",
        ],
    }
)

st.table(df)

st.caption(
    "Hunter Trading Calculator – Qty based · no manual margin input."
)

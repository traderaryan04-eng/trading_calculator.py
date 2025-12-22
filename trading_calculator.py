import streamlit as st
import yfinance as yf
import pandas as pd

# ================== UI CLEANUP (hide footer, menu) ==================
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Hunter Trading Calculator",
    page_icon="💹",
    layout="centered",
)

st.title("💹 Hunter All-in-One Trading Calculator")
st.write("Position Size + PnL + ROE + TP/SL for crypto & stocks.")

# ================== INPUT SECTION ==================
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
        value=50
    )

with col2:
    margin = st.number_input(
        "Capital / Margin (in account currency)",
        min_value=0.0,
        value=100.0
    )
    entry_price = st.number_input(
        "Entry Price",
        min_value=0.0,
        value=0.0,
        help="If 0 hai to live price se entry assume ho sakti hai."
    )
    qty_manual = st.number_input(
        "Quantity (optional, 0 = auto from margin)",
        min_value=0.0,
        value=0.0
    )

col3, col4 = st.columns(2)
with col3:
    tp_price = st.number_input(
        "Take Profit (TP) Price",
        min_value=0.0,
        value=0.0
    )
with col4:
    sl_price = st.number_input(
        "Stop Loss (SL) Price",
        min_value=0.0,
        value=0.0
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
            current_price = 0.0

        info = ticker.info
        currency_code = info.get("currency", "USD") or "USD"  # fallback [web:32][web:41]

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

# Agar user ne entry_price = 0 chhoda hai, to default entry = current_price
if entry_price == 0 and current_price:
    entry_price = current_price

col_lp, col_ep = st.columns(2)
with col_lp:
    st.metric("Live Price", f"{currency_symbol}{current_price:,.2f}")
with col_ep:
    st.metric("Entry Price", f"{currency_symbol}{entry_price:,.2f}")

st.caption(f"Currency detected: {currency_code}")

st.markdown("---")

# ================== CORE CALCULATIONS ==================
# Position size from margin & leverage if qty not given
if entry_price > 0:
    if qty_manual > 0:
        qty = qty_manual
        position_value = qty * entry_price
        required_margin = position_value / leverage if leverage > 0 else position_value
    else:
        position_value = margin * leverage
        qty = position_value / entry_price
        required_margin = margin
else:
    qty = 0.0
    position_value = 0.0
    required_margin = 0.0

def calc_pnl(entry, price, quantity, side_):
    """Simple PnL for long / short."""
    if price == 0 or quantity == 0 or entry == 0:
        return 0.0
    if side_ == "BUY":
        return (price - entry) * quantity
    else:
        return (entry - price) * quantity

# Live PnL, TP PnL, SL PnL
pnl_live = calc_pnl(entry_price, current_price, qty, side)
pnl_tp = calc_pnl(entry_price, tp_price, qty, side) if tp_price > 0 else 0.0
pnl_sl = calc_pnl(entry_price, sl_price, qty, side) if sl_price > 0 else 0.0

# ROE (based on margin used)
if required_margin > 0:
    roe = (pnl_live / required_margin) * 100
else:
    roe = 0.0

# Risk / Reward ratio
risk = abs(pnl_sl)
reward = abs(pnl_tp)
if risk > 0 and reward > 0:
    rr = reward / risk
else:
    rr = 0.0

# ================== POSITION OVERVIEW CARDS ==================
st.subheader("📈 Position Overview")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Quantity", f"{qty:,.4f}")
with col_b:
    st.metric("Position Value", f"{currency_symbol}{position_value:,.2f}")
with col_c:
    st.metric("Required Margin", f"{currency_symbol}{required_margin:,.2f}")

st.markdown("---")

# ================== PnL & RISK METRICS ==================
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

# ================== QUICK SUMMARY TABLE ==================
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

st.caption(
    "Hunter All-in-One Trading Calculator – Position Size + PnL + ROE + TP/SL (Crypto & Stocks)"
)

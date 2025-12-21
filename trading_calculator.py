import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Hunter Trading Calculator", layout="wide")

st.title("🔥 HUNTER TRADING CALCULATOR – ALL IN ONE")
st.markdown("---")

# -------- MARKET BLOCK (MAIN SCREEN – MOBILE FRIENDLY) --------
st.subheader("📊 Market")

colm1, colm2 = st.columns(2)
with colm1:
    symbol = st.text_input(
        "Symbol (ETH-USD / BTC-USD / TATAMOTORS.NS)",
        value="ETH-USD"
    ).upper()

with colm2:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        live_price = float(data["Close"].iloc[-1])
        st.metric("LIVE PRICE", f"{live_price:.2f}")
    except Exception:
        live_price = st.number_input("Manual Price", value=3000.0)
        st.warning("Live price error, manual value used.")

st.markdown("---")

# -------- TRADE INPUTS --------
col1, col2, col3 = st.columns(3)

with col1:
    side = st.radio("Side", ["BUY", "SELL"], horizontal=True)
with col2:
    qty = st.number_input("Quantity", min_value=0.0001, value=1.0, step=0.1)
with col3:
    leverage = st.number_input("Leverage (1–200x)", min_value=1.0, max_value=200.0, value=50.0, step=1.0)

col4, col5, col6 = st.columns(3)
with col4:
    entry_price = st.number_input("Entry Price", value=live_price)
with col5:
    tp_price = st.number_input("Target (TP)", value=round(live_price * 1.02, 2))
with col6:
    sl_price = st.number_input("Stop Loss (SL)", value=round(live_price * 0.98, 2))

# -------- CALCULATION --------
if st.button("🚀 CALCULATE", type="primary"):
    # Required margin & position value
    position_value = qty * entry_price
    required_margin = position_value / leverage if leverage != 0 else 0

    # PnL calculations
    if side == "BUY":
        pnl_live = (live_price - entry_price) * qty
        pnl_tp = (tp_price - entry_price) * qty
        pnl_sl = (sl_price - entry_price) * qty
    else:  # SELL
        pnl_live = (entry_price - live_price) * qty
        pnl_tp = (entry_price - tp_price) * qty
        pnl_sl = (entry_price - sl_price) * qty

    # ROE on margin
    roe = (pnl_live / required_margin) * 100 if required_margin != 0 else 0.0

    # -------- SUMMARY METRICS --------
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("💳 Required Margin", f"${required_margin:,.2f}")
    with c2:
        st.metric("💵 LIVE PnL", f"${pnl_live:,.2f}")
    with c3:
        st.metric("📈 ROE", f"{roe:,.1f}%")

    st.markdown("---")

    # -------- DETAILS --------
    c4, c5 = st.columns(2)

    with c4:
        st.subheader("📦 Position Details")
        st.write(f"**Symbol:** {symbol}")
        st.write(f"**Side:** {side}")
        st.write(f"**Quantity:** {qty:.4f}")
        st.write(f"**Leverage:** {leverage:.1f}x")
        st.write(f"**Position Value:** ${position_value:,.2f}")
        st.write(f"**Entry Price:** ${entry_price:,.2f}")
        st.write(f"**Live Price:** ${live_price:,.2f}")

    with c5:
        st.subheader("🎯 TP / SL Analysis")
        st.write(f"**TP Price:** ${tp_price:,.2f} → **TP PnL:** ${pnl_tp:,.2f}")
        st.write(f"**SL Price:** ${sl_price:,.2f} → **SL PnL:** ${pnl_sl:,.2f}")

        # Risk/Reward
        risk = abs(pnl_sl)
        reward = abs(pnl_tp)
        rr = reward / risk if risk > 0 else 0
        st.write(f"**Risk / Reward:** 1 : {rr:,.2f}")

        if pnl_live > 0:
            st.success("✅ You are in PROFIT right now.")
        else:
            st.error("❌ You are in LOSS right now.")

    # -------- SUMMARY TABLE --------
    st.markdown("---")
    st.subheader("📋 Quick Summary Table")

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
                f\"${required_margin:,.2f}\",
                f\"${position_value:,.2f}\",
                f\"${pnl_live:,.2f}\",
                f\"${pnl_tp:,.2f}\",
                f\"${pnl_sl:,.2f}\",
                f\"{roe:,.1f}%\",
                f\"1 : {rr:,.2f}\",
            ],
        }
    )

    st.table(df)

st.caption("Hunter All-in-One Trading Calculator – Position Size + PnL + ROE + TP/SL")

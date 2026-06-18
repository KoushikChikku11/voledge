import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from models.bs import black_scholes, implied_volatility, vol_smile, vol_term_structure
from data.fetcher import get_all_expirations, get_chain_for_expiry, days_to_expiry, get_spot

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="VolEdge", page_icon="📈", layout="wide")
st.title("📈 VolEdge — Options Analytics Platform")
st.caption("Black-Scholes pricer · Greeks · IV surface · P&L scenarios")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Parameters")
mode        = st.sidebar.radio("Mode", ["Manual", "Live market data"])
option_type = st.sidebar.selectbox("Option type", ["call", "put"])

if mode == "Live market data":
    ticker   = st.sidebar.text_input("Ticker", value="AAPL").upper()
    spot_live = get_spot(ticker)
    if spot_live:
        st.sidebar.metric("Spot price", f"${spot_live:.2f}")
        S = float(spot_live)
    else:
        st.sidebar.warning("Could not fetch price.")
        S = 100.0

    expirations = get_all_expirations(ticker)
    if expirations:
        expiry      = st.sidebar.selectbox("Expiration", expirations)
        T           = days_to_expiry(expiry)
        st.sidebar.caption(f"T = {T:.4f} years")
        calls, puts, _ = get_chain_for_expiry(ticker, expiry)
    else:
        st.sidebar.warning("No options data found.")
        T           = 0.25
        calls, puts = None, None

    K     = st.sidebar.number_input("Strike (K)", value=float(round(S)), step=1.0)
    sigma = st.sidebar.slider("Implied vol (σ)", 0.05, 1.0, 0.25, 0.01)
    r     = st.sidebar.slider("Risk-free rate (r)", 0.0, 0.15, 0.05, 0.005)

else:
    ticker      = None
    calls, puts = None, None
    S     = st.sidebar.number_input("Spot price (S)",  value=100.0, step=1.0)
    K     = st.sidebar.number_input("Strike price (K)", value=100.0, step=1.0)
    T     = st.sidebar.slider("Time to expiry (years)", 0.02, 2.0, 0.25, 0.01)
    sigma = st.sidebar.slider("Implied vol (σ)",        0.05, 1.0,  0.20, 0.01)
    r     = st.sidebar.slider("Risk-free rate (r)",     0.0,  0.15, 0.05, 0.005)

# ── Compute ───────────────────────────────────────────────────────────────────
price, delta, gamma, vega, theta, rho, d1, d2 = black_scholes(S, K, T, r, sigma, option_type)
intrinsic = max(S - K, 0.0) if option_type == "call" else max(K - S, 0.0)
time_val  = price - intrinsic

# ── Metrics ───────────────────────────────────────────────────────────────────
st.subheader("Output")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Option Price",    f"${price:.4f}")
c2.metric("Intrinsic Value", f"${intrinsic:.2f}")
c3.metric("Time Value",      f"${time_val:.4f}")
c4.metric("d₁",              f"{d1:.4f}")
c5.metric("d₂",              f"{d2:.4f}")
c6.metric("Moneyness", "ITM" if intrinsic > 0 else ("ATM" if S == K else "OTM"))

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Greeks", "Payoff diagram", "Vol surface", "P&L scenarios", "Options chain"])

# ── Tab 1: Greeks ─────────────────────────────────────────────────────────────
with tab1:
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("Delta (Δ)", f"{delta:.4f}", help="Price change per $1 move in spot")
    g2.metric("Gamma (Γ)", f"{gamma:.4f}", help="Rate of change of delta")
    g3.metric("Vega (ν)",  f"{vega:.4f}",  help="Price change per 1% move in vol")
    g4.metric("Theta (Θ)", f"{theta:.4f}", help="Daily time decay")
    g5.metric("Rho (ρ)",   f"{rho:.4f}",   help="Price change per 1% move in rates")

    st.subheader("Greeks vs Spot")
    spot_range  = np.linspace(S * 0.6, S * 1.4, 100)
    greek_choice = st.selectbox("Select Greek", ["Delta", "Gamma", "Vega", "Theta"])
    idx_map     = {"Delta": 1, "Gamma": 2, "Vega": 3, "Theta": 4}
    greek_vals  = [black_scholes(float(s), K, T, r, sigma, option_type)[idx_map[greek_choice]] for s in spot_range]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=spot_range, y=greek_vals, mode='lines', line=dict(color='#378ADD', width=2)))
    fig.add_vline(x=S, line_dash="dash", line_color="gray", annotation_text="Current spot")
    fig.update_layout(xaxis_title="Spot price", yaxis_title=greek_choice, height=350, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: Payoff ─────────────────────────────────────────────────────────────
with tab2:
    spot_range    = np.linspace(S * 0.6, S * 1.4, 200)
    prices_now    = [black_scholes(float(s), K, T,      r, sigma, option_type)[0] for s in spot_range]
    prices_expiry = [black_scholes(float(s), K, 0.0001, r, sigma, option_type)[0] for s in spot_range]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=spot_range, y=prices_now,    mode='lines', name='Today',     line=dict(color='#378ADD', width=2)))
    fig2.add_trace(go.Scatter(x=spot_range, y=prices_expiry, mode='lines', name='At expiry', line=dict(color='#1D9E75', width=2, dash='dash')))
    fig2.add_vline(x=S, line_dash="dot", line_color="gray",   annotation_text="Spot")
    fig2.add_vline(x=K, line_dash="dot", line_color="orange", annotation_text="Strike")
    fig2.update_layout(xaxis_title="Spot price ($)", yaxis_title="Option value ($)", height=400, margin=dict(t=20))
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 3: Vol surface ────────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Vol smile")
        strikes = np.linspace(S * 0.7, S * 1.3, 40)
        smile   = vol_smile(S, T, r, sigma, strikes)
        ks, ivs = zip(*smile)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=list(ks), y=[v * 100 for v in ivs], mode='lines+markers', line=dict(color='#378ADD', width=2), marker=dict(size=4)))
        fig3.add_vline(x=K, line_dash="dash", line_color="orange", annotation_text="Strike")
        fig3.update_layout(xaxis_title="Strike ($)", yaxis_title="Implied vol (%)", height=350, margin=dict(t=20))
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.subheader("Term structure")
        expiry_days = [1, 7, 14, 30, 60, 90, 120, 180, 270, 365]
        expiry_yrs  = [d / 365 for d in expiry_days]
        term        = vol_term_structure(S, K, r, sigma, expiry_yrs)
        ts, tvs     = zip(*term)
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=list(ts), y=[v * 100 for v in tvs], mode='lines+markers', line=dict(color='#D85A30', width=2), marker=dict(size=4)))
        fig4.update_layout(xaxis_title="Days to expiry", yaxis_title="Implied vol (%)", height=350, margin=dict(t=20))
        st.plotly_chart(fig4, use_container_width=True)

# ── Tab 4: P&L scenarios ──────────────────────────────────────────────────────
with tab4:
    st.subheader("P&L at expiry — 1 contract (100 shares)")
    moves = [-30, -20, -15, -10, -5, -2, 2, 5, 10, 15, 20, 30]
    rows  = []
    for pct in moves:
        new_s      = S * (1 + pct / 100)
        exit_price = black_scholes(float(new_s), K, 0.0001, r, sigma, option_type)[0]
        pnl        = (exit_price - price) * 100
        rows.append({
            "Spot move":  f"{'+' if pct > 0 else ''}{pct}%",
            "New spot":   f"${new_s:.2f}",
            "Exit price": f"${exit_price:.4f}",
            "P&L":        f"${pnl:+.2f}"
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Tab 5: Options chain ──────────────────────────────────────────────────────
with tab5:
    if calls is not None and puts is not None:
        st.subheader(f"Live options chain — {ticker}")
        col_c, col_p = st.columns(2)
        with col_c:
            st.caption("Calls")
            st.dataframe(calls.reset_index(drop=True), use_container_width=True, hide_index=True)
        with col_p:
            st.caption("Puts")
            st.dataframe(puts.reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        st.info("Switch to **Live market data** mode in the sidebar to see the options chain.")
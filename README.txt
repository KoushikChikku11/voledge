# VolEdge — Options Analytics Platform

A live options analytics platform implementing Black-Scholes pricing, Greeks, and implied volatility surfaces from scratch in Python.

**Live app:** [v0ledge.streamlit.app](https://v0ledge.streamlit.app)

---

## What it does

VolEdge prices options and surfaces the risk metrics professional traders use daily — built entirely from the underlying math rather than a pricing library.

- **Black-Scholes pricer** — analytical d₁/d₂ computation and option pricing, implemented from the closed-form solution rather than a library call
- **Greeks dashboard** — Delta, Gamma, Vega, Theta, and Rho, all derived analytically and visualized against spot price
- **Implied volatility solver** — Newton-Raphson root-finding to back out IV from a market price
- **Vol smile & term structure** — parametric models showing how implied vol varies across strikes and expiries
- **P&L scenario simulator** — payoff and profit/loss across a range of spot price moves
- **Live market data** — real-time options chains, spot prices, and expirations pulled via the yfinance API for any ticker

---

## Why I built it

I wanted to understand options pricing at the level traders actually use it — not just the formula, but the numerical methods (IV solving), the visualizations (vol surfaces), and the engineering (a real deployed app) around it. This project is the result.

---

## Tech stack

| Layer | Tools |
|---|---|
| Math core | Python, NumPy, SciPy |
| Data | yfinance (live options chains) |
| Front-end | Streamlit, Plotly |
| Deployment | Streamlit Community Cloud |

---

## Project structure

```
voledge/
├── app.py                 # Streamlit front-end — all UI and tabs
├── models/
│   └── bs.py               # Black-Scholes pricer, Greeks, IV solver, vol surface models
├── data/
│   └── fetcher.py           # Live market data via yfinance
└── requirements.txt
```

---

## Running it locally

```bash
git clone https://github.com/KoushikChikku11/voledge.git
cd voledge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## The math

**Black-Scholes:**

```
C = S·N(d₁) − K·e^(−rT)·N(d₂)
P = K·e^(−rT)·N(−d₂) − S·N(−d₁)

d₁ = [ln(S/K) + (r + σ²/2)·T] / (σ·√T)
d₂ = d₁ − σ·√T
```

**Implied volatility** is solved iteratively via Newton-Raphson, inverting the pricing formula to find the σ that produces a given market price.

---

## Disclaimer

European-style options, no dividends. Built for educational purposes and as a demonstration of quantitative finance fundamentals — not intended for live trading decisions.

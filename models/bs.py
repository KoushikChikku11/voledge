import numpy as np
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    Black-Scholes option pricer.
    S     : spot price
    K     : strike price
    T     : time to expiry in years
    r     : risk-free rate (decimal)
    sigma : implied volatility (decimal)
    """
    if T <= 0:
        if option_type == 'call':
            return max(S - K, 0), 0, 0, 0, 0, 0, 0, 0
        else:
            return max(K - S, 0), 0, 0, 0, 0, 0, 0, 0

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        rho   = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
        rho   = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega  = S * norm.pdf(d1) * np.sqrt(T) / 100
    theta = (
        (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * norm.cdf(d2))
        / 365
    ) if option_type == 'call' else (
        (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * norm.cdf(-d2))
        / 365
    )

    return price, delta, gamma, vega, theta, rho, d1, d2


def implied_volatility(market_price, S, K, T, r, option_type='call'):
    """
    Newton-Raphson IV solver.
    Backs out implied vol from a market price.
    """
    sigma = 0.2  # initial guess
    for _ in range(100):
        price, _, _, vega, _, _, _, _ = black_scholes(S, K, T, r, sigma, option_type)
        vega_raw = vega * 100  # undo the /100 scaling
        diff = price - market_price
        if abs(diff) < 1e-6:
            break
        if vega_raw < 1e-10:
            break
        sigma -= diff / vega_raw
        sigma = max(0.001, min(sigma, 10.0))  # keep in bounds
    return sigma


def vol_smile(S, T, r, base_sigma, strikes):
    """
    Parametric vol smile — skew + smile around ATM.
    Returns list of (strike, iv) pairs.
    """
    results = []
    for K in strikes:
        moneyness = (K - S) / S
        skew = base_sigma + 0.08 * moneyness**2 - 0.03 * moneyness
        skew = max(0.05, skew)
        results.append((K, skew))
    return results


def vol_term_structure(S, K, r, base_sigma, expiries):
    """
    Parametric vol term structure.
    Returns list of (expiry_days, iv) pairs.
    """
    results = []
    for T in expiries:
        term = base_sigma * (1 + 0.1 * np.exp(-3 * T) - 0.05 * T)
        term = max(0.05, term)
        results.append((round(T * 365), term))
    return results
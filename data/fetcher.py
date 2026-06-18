import yfinance as yf
import pandas as pd
import numpy as np


def get_options_chain(ticker: str):
    """
    Fetches live options chain for a given ticker.
    Returns calls and puts dataframes + current spot price.
    """
    try:
        stock = yf.Ticker(ticker)
        spot = stock.fast_info['lastPrice']
        expirations = stock.options

        if not expirations:
            return None, None, None, None

        # Use the nearest expiration by default
        expiry = expirations[0]
        chain = stock.option_chain(expiry)

        calls = chain.calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].copy()
        puts  = chain.puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].copy()

        calls.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']
        puts.columns  = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']

        # Convert IV to percentage for display
        calls['IV'] = (calls['IV'] * 100).round(2)
        puts['IV']  = (puts['IV'] * 100).round(2)

        return calls, puts, spot, expiry

    except Exception as e:
        return None, None, None, str(e)


def get_all_expirations(ticker: str):
    """Returns list of all available expiration dates for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        return list(stock.options)
    except:
        return []


def get_chain_for_expiry(ticker: str, expiry: str):
    """Fetches options chain for a specific expiration date."""
    try:
        stock = yf.Ticker(ticker)
        spot = stock.fast_info['lastPrice']
        chain = stock.option_chain(expiry)

        calls = chain.calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].copy()
        puts  = chain.puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].copy()

        calls.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']
        puts.columns  = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'OI', 'IV']

        calls['IV'] = (calls['IV'] * 100).round(2)
        puts['IV']  = (puts['IV'] * 100).round(2)

        return calls, puts, spot

    except Exception as e:
        return None, None, None


def days_to_expiry(expiry_str: str) -> float:
    """Converts expiry date string to years (T for Black-Scholes)."""
    expiry = pd.Timestamp(expiry_str)
    today  = pd.Timestamp.today()
    days   = (expiry - today).days
    return max(days / 365, 0.0001)


def get_spot(ticker: str) -> float:
    """Returns current spot price for a ticker."""
    try:
        return yf.Ticker(ticker).fast_info['lastPrice']
    except:
        return None
import streamlit as st
import yfinance as yf
import pandas as pd

# TTL is set to 7200 seconds (2 hours)
CACHE_TIME = 7200 

@st.cache_data(ttl=CACHE_TIME)
def get_spy_data():
    # Fetches SPY historical data
    return yf.download('SPY', period='10y', auto_adjust=True, progress=False)

@st.cache_data(ttl=CACHE_TIME)
def get_vix_data():
    # Fetches VIX historical data
    return yf.download('^VIX', period='10y', auto_adjust=True, progress=False)

@st.cache_data(ttl=CACHE_TIME)
def get_sh_data():
    # Fetches SPY and IEF for Safe Haven Demand
    return yf.download(['SPY', 'IEF'], period='10y', auto_adjust=True, progress=False)['Close']

@st.cache_data(ttl=CACHE_TIME)
def get_gv_data():
    # Fetches SPY, IVW, and IVE for Growth vs Value analysis
    return yf.download(['SPY', 'IVW', 'IVE'], period='10y', auto_adjust=True, progress=False)['Close']

@st.cache_data(ttl=CACHE_TIME)
def get_options_data(ticker_symbol='SPY'):
    # Fetches option chains for the nearest 14 expirations
    ticker = yf.Ticker(ticker_symbol)
    dates = ticker.options[:14]
    chains = []
    for date in dates:
        opt = ticker.option_chain(date)
        chains.append({
            'date': date,
            'calls': opt.calls,
            'puts': opt.puts
        })
    # Also return current price to avoid extra calls in main
    current_price = ticker.history(period="1d")['Close'].iloc[-1]
    return chains, current_price

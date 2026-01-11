# Cy's Market Sentiment Dashboard

A real-time financial sentiment gauge that aggregates multiple data points into a single "Fear & Greed" index for the U.S. Stock Market.
Aimed to complement CNN's Fear and Greed Index by:
  1. Modified core components for computing sentiments
  2. Interactive 10-year charts for each component
  3. Diagnostics on options activities

## Live Application
**[View Live Dashboard](https://cy-market-sentiment-dashboard.streamlit.app)**

## Methodology
This dashboard calculates a weighted sentiment score (0-100) based on four key market pillars:

1. **Market Trend**: S&P 500 price relative to its 125-day Moving Average.
2. **Volatility**: VIX Index movement relative to its 50-day trend.
3. **Asset Allocation**: 20-day yield spread between Stocks ($SPY) and Treasury Bonds ($IEF).
4. **Institutional Rotation**: Performance deviation between Growth ($IVW) and Value ($IVE) stocks.

Also featuring diagnostics for **Options Activity**, including Put/Call ratios and Volatility Skew visualization for the nearest 14 expiration dates.

## Tech Stack
- **Language:** Python
- **Framework:** Streamlit
- **Data Source:** Yahoo Finance (`yfinance`)
- **Plots:** Plotly Interactive Charts

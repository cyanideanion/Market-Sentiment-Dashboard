# Market Sentiment Dashboard & Conditional Return Analysis

## Overview
This project develops a stock market sentiment diagnosis through aggregating multiple macro-financial indicators into interpretable sentiment labels (Extreme Fear, Greed, Neutral, Greed, Extreme Greed), and examines how these labels coincided with market behaviors historically.

The purpose of the project is **not to propose a trading strategy and thus does not constitute any financial advices**, but to explore:
- how sentiment indicators co-move with market dynamics,
- how long extreme sentiment state tend to persist, 
- how different sentiment aligned with subsequent return distributions across different time horizons.

## Live Application
**[View Live Dashboard](https://cy-market-sentiment-dashboard.streamlit.app)**

## Motivation
Greed and fear, as part of “animal spirits”, are mental instincts that deviate economic decisions from rationality and efficiency. This theory was coined by John Maynard Keynes in his book *The General Theory of Employment, Interest and Money (1936)*, and maintained its popularity among studies in behavioral economics and behavioral finance today. 

However, many sentiment tools are either:
- opaque composites with little interpretability, or
- presented in a way that encourages overfitting and performance chasing.

This project was built to bridge that gap by combining:
- transparent indicator construction and calculation methods
- 10 years lookback window
- research-style exploratory analysis.

## Key Features
### Sentiment Construction
The aggregate sentiment score integrates multiple market-based indicators, including:
- equity trend deviation (SPY vs moving averages),
- implied volatility (VIX),
- yield spreads (risk-free vs equities),
- sector rotation dynamics.

Indicators are standardized and combined into a composite sentiment score, which is then discretized into five labels:

**Extreme Fear, Fear, Neutral, Greed, Extreme Greed.**

### Interactive Plots
The dashboard allows users to:
- compare trends across different market sentiments in the past decade,
- examine co-movement between sentiment changes and market movements,
- explore historical incidents of sentiment dislocation.

### Research Appendix (Descriptive Analysis)
An optional research appendix applies empirical tools commonly used in economic research:
1. **Correlation Analysis:** testing reliability of the aggregate sentiment score and decoupling incidents through examining the 60-day rolling correlations between standardized sentiment changes and SPY returns
2. **Recovery Time Analysis:** studies the distribution of calendar days required for sentiment to recover from “Extreme Fear” to “Neutral”
3. **Forward Performance Analysis:** examination of forward return distributions conditional on sentiment states while focusing on risk–return asymmetry rather than performance ranking.

*All analyses are retrospective, assumption-dependent, and intended for educational and research purposes only.*

## Technical Stack
- **Language:** Python
- **Visualization:** Plotly
- **Dashboard:** Streamlit
- **Data:** yfinance

## Disclaimer
This project is for **research purposes only.** It does not constitute investment advice, trading recommendations, or performance claims.

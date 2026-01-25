# research_content.py

RESEARCH_APPENDIX = {
    "correlation_analysis": {
        "method": """
            **Method:** The analysis observes the 60-day rolling correlation of the standardized daily percentage changes (Z-scores) for both the Market Sentiment Score and SPY. 
            By using Z-scores, the data is normalized to a mean of 0 and a standard deviation of 1, 
            allowing for a direct comparison of volatility and movement despite the different original scales of the two metrics.
        """,
        "results": """
            **Results:** 
            \n- **Positive Relationship:** The correlation coefficient consistently remains in positive territory, generally fluctuating between 0.4 and 0.9.
            \n- **Stability:** For the majority of the period from 2017 to 2026, the correlation is robust, frequently hovering near the 0.7 to 0.9 range.
            \n- **Significant Deviations:** Notable “dips” in correlation occurred in early 2020 and early 2025, where the coefficient briefly dropped toward 0.4 to 0.55.
        """,
        "discussion": """
        **Discussion:** The high rolling correlation suggests that the Market Sentiment Score is a strong co-movement indicator for SPY. 
        When sentiment shifts significantly (as seen in the red spikes/dips in the top pane), the SPY (blue lines) tends to follow suit in the same direction. 
        \n However, the periodic sharp drops in the correlation coefficient should be critically examined. 
        These "decoupling" events indicate periods where the Sentiment Score does not accurately reflect the magnitude of movements in the actual stock market, 
        found in timeframes of exogenous shocks (COVID-19) or specific technical trading patterns (TACO trade) where price determination is driven by factors 
        beyond market trend and asset allocation displayed in the previous tabs. 
        """
    },
    "recovery_analysis": {
        "method": """
            **Method:** The analysis utilizes a combination of a scatter plot and a box plot to visualize the distribution of calendar days 
            between the first occurrence of an “Extreme Fear” aggregate sentiment to recovering to a “Neutral” sentiment." 
            The scatter plot shows individual data points to highlight density and outliers, while the box plot provides a statistical summary of the central tendency and spread.
        """,
        "results": """
            **Results:** \n- **Average Recovery Time:** The median time between an “Extreme Fear” occurring to the first “Neutral” after that “Extreme Fear” is 24 days (the horizontal line within the box). 
            \n- **Interquartile Range (IQR):** The middle 50% of recovery events occur between 13 and 37 days. 
            \n- **Full Range:** Recovery times vary significantly, ranging from near-instantaneous (approximately 1 day) to a maximum of 99 days (as seen in the highest outlier). 
            \n- **Typical Outliers:** While most recoveries happen within 40 days, there is a visible cluster of events taking between 40 and 80 days.
        """,
        "discussion": """
            **Discussion:** The Sentiment Score is a function of cross-asset correlation. Time required for arbitrage and rebalancing to occur across these sectors should be considered while examining the recovery distribution. For instance: 
            \n- **VIX Mean Reversion:** Implied volatility spikes and decays in a square-root process, meaning fearful sentiment reflected through option activities typically follow a speedy recovery. 
            \n- **Bonds-Stocks Spread Normalization:** Shift in interest rate expectations or inflationary outlooks that are influenced by monthly macroeconomic data releases, explaining the 20–30 day clustering. 
            \n- **Style Rotation Frictions:** Investor favoritism towards growth versus value companies relates closely to macroeconomic conditions (e.g. discount rate). A recovery to "Neutral" implies that the market has reached a new consensus on the cost of capital, which does have a strict timeframe pattern.
        """
    },
    "forward_performance": {
        "method": """
            **Method:** This analysis observes the distribution of forward returns of the stock market categorized by the five sentiment regimes: 
            Extreme Fear, Fear, Neutral, Greed, and Extreme Greed, across the time horizons of 1, 3, 6, and 12 months through a comparative box plot with outliers in scatter points.
        """,
        "results": """
            **Results:** \n- **Direct Correlation with Time:** Across all sentiment labels, the median forward return (indicated by the solid horizontal line within boxes) 
            trends upward as the time horizon extends from 1 month to 12 months. Data dispersion across different sentiments also amplifies as the horizon increases. 
            \n- **Extreme Greed Outperformance:** The "Extreme Greed" sentiment exhibits a significantly higher return across all quartiles than other sentiments in the 12-month horizon, and a relatively low variance in the 1-month horizon. 
            \n- **Extreme Fear Leptokurtosis:** The "Extreme Fear" sentiment exhibits a highly concentrated 12-month forward performance relative to other sentiments, 
            with an IQR of only 7.7%. Additionally, "Extreme Fear" has the largest variance than other sentiments in the 1-month horizon, but gradually skews toward leptokurtosis as horizon increases. 
            \n- **Fearful Sentiment Dispersion:** The "Fear" sentiment exhibits the highest return variance in the 12-month horizon compared to other sentiments, but also the lowest mean and median return compared to other sentiments in the 12-month horizon. 
            \n- **Neutral/Greed Convergence:** The 12-month forward returns for "Neutral" and "Greed" are statistically similar, both clustering around a 16% median with an IQR of 13.6% and 15.8% respectively. Additionally, “Neutral” has a relatively low variance in the 1-month horizon.
        """,
        "discussion": """
            **Discussion:** Similar to the Recovery Time Analysis, this study examines outcomes in relation of time that are closely dependent on the nature of different asset classes. 
            From this standpoint, the sentiment spectrum measures the relative degree of risk aversion in the financial market. 
            And two hypotheses regarding market efficiency and behavioral economics can be extracted through this analysis of forward performance: 
            \n- **Extreme Fear and Risk Premium:** All four indicators (SPY MA, VIX MA, Yield Spreads, Sector Rotation) trigger “Extreme Fear” often signifies a liquidity-driven dislocation, 
            where stocks are perceived as extremely risky and equity risk premium at its highest. Contrarian investments during these periods would follow a classic high-risk, 
            high-reward profile: while 12-month return is relatively robust with minimal variance, short-term (1 to 3 months) volatility are significantly elevated. 
            \n- **Equilibrium at Extreme Greed:** A common heuristic bias is to assume that "Extreme Greed" is a precursor to an immediate crash. 
            However, the data suggests that "Extreme Greed" actually produces the highest median 12-month returns with narrower dispersion than the “Fear” sentiment. 
            This is due to, when the four indicators align in a steady "Greed" state, uptrend technical trading patterns with high confidence in the macroeconomic conditions consolidate 
            structural stability rather than raising the fear of a crash. Therefore, the systemic risk of an “Extreme Greed” market is primarily the eventual shifts toward 
            the "Neutral" state with uncertainty in either direction, and not a sudden crash in most cases for the past decade.
        """,
    }

}
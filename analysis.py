import pandas as pd

# Sentiment label functions for individual indicators (also used in tabs)

THRESHOLD_VALUE = ["Extreme Greed","Greed","Neutral","Fear","Extreme Fear"]

overall_threshold = [76,56,45,25]
spy_threshold = [76,56,45,25]
vix_threshold = [95,80,20,5]
sh_threshold = [75,60,40,25]
gv_threshold = [90,70,40,20]

def get_sentiment_label(s, threshold):
    """Categorizes the 0-100 average into a sentiment string."""
    for i in range(4):
        if s >= threshold[i]: return THRESHOLD_VALUE[i]
    return THRESHOLD_VALUE[-1]

def get_overall_sentiment_string(s):
    return get_sentiment_label(s, overall_threshold)

def get_spy_sentiment_string(s):
    return get_sentiment_label(s, spy_threshold)

def get_vix_sentiment_string(s):
    return get_sentiment_label(s, vix_threshold)

def get_sh_sentiment_string(s):
    return get_sentiment_label(s, sh_threshold)

def get_gv_sentiment_string(s):
    return get_sentiment_label(s, gv_threshold)

def calculate_sentiment(df_spy, vix_data, sh_data, gv_data):
    df_spy = df_spy.copy()
    vix_data = vix_data.copy()
    sh_data = sh_data.copy()
    gv_data = gv_data.copy()

    # 1. SPY technical momentum
    if isinstance(df_spy.columns, pd.MultiIndex):
        df_spy.columns = df_spy.columns.get_level_values(0)

    df_spy["125MA"] = df_spy["Close"].rolling(window=125).mean()
    df_spy["Diff"] = df_spy["Close"] - df_spy["125MA"]
    df_spy["Score"] = (
        df_spy["Diff"].rolling(window=365).rank(pct=True) * 100
    )
    df_spy["Sentiment"] = df_spy["Score"].apply(
        get_spy_sentiment_string
    )

    # 2. VIX trend
    if isinstance(vix_data.columns, pd.MultiIndex):
        vix_data.columns = vix_data.columns.get_level_values(0)

    vix_df = vix_data[["Close"]].copy()
    vix_df["50MA"] = vix_df["Close"].rolling(window=50).mean()
    vix_df["Diff"] = vix_df["Close"] - vix_df["50MA"]
    vix_df["Percentile"] = (
        vix_df["Diff"].rolling(window=252).rank(pct=True) * 100
    )
    vix_df["Calculated_Score"] = 100 - vix_df["Percentile"]
    vix_df["Sentiment"] = vix_df["Calculated_Score"].apply(
        get_vix_sentiment_string
    )

    # 3. Safe-haven demand
    if isinstance(sh_data.columns, pd.MultiIndex):
        sh_data.columns = sh_data.columns.get_level_values(0)

    sh_returns = sh_data.pct_change(20).dropna()
    # "IEF" = iShares 7-10 Year Treasury Bond ETF 
    sh_returns["Spread"] = sh_returns["SPY"] - sh_returns["IEF"]
    sh_returns["Score"] = (
        sh_returns["Spread"].rolling(window=252).rank(pct=True) * 100
    )
    sh_returns["Sentiment"] = sh_returns["Score"].apply(
        get_sh_sentiment_string
    )

    # 4. Growth versus value
    if isinstance(gv_data.columns, pd.MultiIndex):
        gv_data.columns = gv_data.columns.get_level_values(0)

    gv_returns = gv_data.pct_change(periods=252)
    gv_dev = pd.DataFrame(index=gv_returns.index)

    # "IVW" = iShares S&P 500 Growth ETF
    gv_dev["IVW_dev"] = (gv_returns["IVW"] - gv_returns["SPY"]) * 100
    # "IVE" = iShares S&P 500 Value ETF
    gv_dev["IVE_dev"] = (gv_returns["IVE"] - gv_returns["SPY"]) * 100
    gv_dev["Diff"] = gv_dev["IVW_dev"] - gv_dev["IVE_dev"]
    gv_dev["Score"] = (
        gv_dev["Diff"].rolling(window=252).rank(pct=True) * 100
    )
    gv_dev["Sentiment"] = gv_dev["Score"].apply(
        get_gv_sentiment_string
    )

    # 5. Combine the four indicator scores
    spy_scores = df_spy[["Score"]].rename(
        columns={"Score": "spy_score"}
    )
    vix_scores = vix_df[["Calculated_Score"]].rename(
        columns={"Calculated_Score": "vix_score"}
    )
    sh_scores = sh_returns[["Score"]].rename(
        columns={"Score": "sh_score"}
    )
    gv_scores = gv_dev[["Score"]].rename(
        columns={"Score": "gv_score"}
    )

    combined_sentiment_df = pd.concat(
        [spy_scores, vix_scores, sh_scores, gv_scores],
        axis=1,
        join="outer",
    )

    combined_sentiment_df["overall_average_sentiment"] = (
        combined_sentiment_df[
            ["spy_score", "vix_score", "sh_score", "gv_score"]
        ].mean(axis=1)
    )

    combined_sentiment_df["overall_label"] = (
        combined_sentiment_df["overall_average_sentiment"].apply(
            get_overall_sentiment_string
        )
    )

    return {
        "spy": df_spy,
        "vix": vix_df,
        "safe_haven": sh_returns,
        "growth_value": gv_dev,
        "combined": combined_sentiment_df,
    }

import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go
from datetime import datetime as dt

# ==========================================
# Page Configuration
# ==========================================
st.markdown("""
    <style>
        .stTabs {
            background-color: #f9f9f9;
            padding: 1rem;
            border-radius: 15px;

        }
        div[data-baseweb="tab-list"] {
            background-color: #eeeeee;
            border-radius: 10px 10px 0 0;
            padding: 5px;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Market Sentiment Dashboard", layout="wide")

st.title("U.S. Stock Market Sentiment Dashboard")

# --- Spectrum at Top of Page ---
def sentiment_legend_custom_text():
    bg_red = "#FFE9E9"
    bg_blue = "#E8F2FF"
    bg_green = "#E8F9EE"

    text_color_red = "#BD4043"
    text_color_blue = "#0054A3"  # Example: Bright yellow text for Neutral
    text_color_green = "#158237"

    st.markdown(
        f"""
        <style>
        .spectrum-container {{
            display: flex;
            width: 100%;
            height: 50px;
            border-radius: 10px;
            overflow: hidden;
            font-family: 'Source Sans Pro', sans-serif;
        }}
        .segment {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 500;
            text-align: center;
            padding: 2px;
            border-right: 1px solid rgba(255,255,255,0.2);
        }}
        .segment:last-child {{
            border-right: none;
        }}
        </style>

        <div class="spectrum-container">
            <div class="segment" style="background-color: {bg_red}; color: {text_color_red};">
                <span class="label-text">Extreme Fear<br>(0-24)</span>
            </div>
            <div class="segment" style="background-color: {bg_red}; color: {text_color_red};">
                <span class="label-text">Fear<br>(25-44)</span>
            </div>
            <div class="segment" style="background-color: {bg_blue}; color: {text_color_blue};">
                <span class="label-text">Neutral<br>(45-55)</span>
            </div>
            <div class="segment" style="background-color: {bg_green}; color: {text_color_green};">
                <span class="label-text">Greed<br>(56-75)</span>
            </div>
            <div class="segment" style="background-color: {bg_green}; color: {text_color_green};">
                <span class="label-text">Extreme Greed<br>(76-100)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

sentiment_legend_custom_text()

# ==========================================
# Current Aggregate Sentiment Calculation and Plotting
# ==========================================

# Sentiment label functions for individual indicators (also used in tabs)

def get_overall_sentiment_label(s):
    """Categorizes the 0-100 average into a sentiment string."""
    if s >= 76: return "Extreme Greed"
    elif s >= 56: return "Greed"
    elif s >= 45: return "Neutral"
    elif s >= 25: return "Fear"
    else: return "Extreme Fear"

def get_spy_sentiment_string(s):
    if s >= 75: return "Extreme Greed"
    elif s >= 55: return "Greed"
    elif s >= 45: return "Neutral"
    elif s >= 25: return "Fear"
    else: return "Extreme Fear"

def get_vix_sentiment_string(s):
    if s >= 95: return "Extreme Greed"
    elif s >= 80: return "Greed"
    elif s >= 20: return "Neutral"
    elif s >= 5: return "Fear"
    else: return "Extreme Fear"

def get_sh_sentiment_string(score):
    if score <= 25: return "Extreme Fear"
    elif score <= 40: return "Fear"
    elif score <= 60: return "Neutral"
    elif score <= 75: return "Greed"
    else: return "Extreme Greed"

def get_gv_sentiment_string(s):
    if s >= 90: return "Extreme Greed"
    elif s >= 70: return "Greed"
    elif s >= 40: return "Neutral"
    elif s >= 20: return "Fear"
    else: return "Extreme Fear"

# --- Data Fetching & Score Calculation ---

# Tab1 Col1. S&P 500 Trend
df_spy = yf.download('SPY', period='10y', auto_adjust=True, progress=False)
if isinstance(df_spy.columns, pd.MultiIndex):
    df_spy.columns = df_spy.columns.get_level_values(0)
df_spy['125MA'] = df_spy['Close'].rolling(window=125).mean()
df_spy['Diff'] = df_spy['Close'] - df_spy['125MA']
df_spy['Score'] = df_spy['Diff'].rolling(window=365).rank(pct=True) * 100
df_spy['Sentiment'] = df_spy['Score'].apply(get_spy_sentiment_string)

# Tab1 Col2. VIX Trend (Inverted)
vix_data = yf.download('^VIX', period='10y', auto_adjust=True, progress=False)
if isinstance(vix_data.columns, pd.MultiIndex):
    vix_data.columns = vix_data.columns.get_level_values(0)
vix_df = vix_data[['Close']].copy()
vix_df['50MA'] = vix_df['Close'].rolling(window=50).mean()
vix_df['Diff'] = vix_df['Close'] - vix_df['50MA']
vix_df['Percentile'] = vix_df['Diff'].rolling(window=252).rank(pct=True) * 100
vix_df['Calculated_Score'] = 100 - vix_df['Percentile']
vix_df['Sentiment'] = vix_df['Calculated_Score'].apply(get_vix_sentiment_string)

# Tab2 Col1. Safe Haven Demand
sh_data = yf.download(['SPY', 'IEF'], period='10y', auto_adjust=True, progress=False)['Close']
if isinstance(sh_data.columns, pd.MultiIndex):
    sh_data.columns = sh_data.columns.get_level_values(0)
sh_returns = sh_data.pct_change(20).dropna()
sh_returns['Spread'] = sh_returns['SPY'] - sh_returns['IEF']
sh_returns['Score'] = sh_returns['Spread'].rolling(window=252).rank(pct=True) * 100
sh_returns['Sentiment'] = sh_returns['Score'].apply(get_sh_sentiment_string)

# Tab2 Col2. Growth vs Value
gv_data = yf.download(['SPY', 'IVW', 'IVE'], period='10y', auto_adjust=True, progress=False)['Close']
if isinstance(gv_data.columns, pd.MultiIndex):
    gv_data.columns = gv_data.columns.get_level_values(0)
gv_returns = gv_data.pct_change(periods=252)
gv_dev = pd.DataFrame(index=gv_returns.index)
gv_dev['IVW_dev'] = (gv_returns['IVW'] - gv_returns['SPY']) * 100
gv_dev['IVE_dev'] = (gv_returns['IVE'] - gv_returns['SPY']) * 100
gv_dev['Diff'] = gv_dev['IVW_dev'] - gv_dev['IVE_dev']
gv_dev['Score'] = gv_dev['Diff'].rolling(window=252).rank(pct=True) * 100
gv_dev['Sentiment'] = gv_dev['Score'].apply(get_gv_sentiment_string)

# --- Combine and Average Scores ---
spy_scores = df_spy[['Score']].rename(columns={'Score': 'spy_score'})
vix_scores = vix_df[['Calculated_Score']].rename(columns={'Calculated_Score': 'vix_score'})
sh_scores = sh_returns[['Score']].rename(columns={'Score': 'sh_score'})
gv_scores = gv_dev[['Score']].rename(columns={'Score': 'gv_score'})

combined_sentiment_df = pd.concat([spy_scores, vix_scores, sh_scores, gv_scores], axis=1, join='outer')
# Calculate the simple average across all four indicators
combined_sentiment_df['overall_average_sentiment'] = combined_sentiment_df[['spy_score', 'vix_score', 'sh_score', 'gv_score']].mean(axis=1)
# Categorize based on user-defined ranges
combined_sentiment_df['overall_label'] = combined_sentiment_df['overall_average_sentiment'].apply(get_overall_sentiment_label)

# Get current score
latest_score = combined_sentiment_df['overall_average_sentiment'].iloc[-1]
latest_label = combined_sentiment_df['overall_label'].iloc[-1]

# Display Current Aggregate Sentiment
st.subheader(" ")
st.header("Current Aggregate Sentiment")
col_stat, col_chart = st.columns([1, 3])

with col_stat:
    if latest_label == "Extreme Greed": st.success(f"**{latest_label}**")
    elif latest_label == "Greed": st.success(f"**{latest_label}**")
    elif latest_label == "Neutral": st.info(f"**{latest_label}**")
    elif latest_label == "Fear": st.error(f"**{latest_label}**")
    else: st.error(f"**{latest_label}**")

    st.metric("Aggregate Score", f"{latest_score:.0f}/100")
    #st.write("This score is the simple average of all four market indicators.")

with col_chart:
    # --- Historical Market Sentiment Plot ---
    fig_overall_sentiment = go.Figure()

    fig_overall_sentiment.add_trace(go.Scatter(
        x=combined_sentiment_df.index,
        y=combined_sentiment_df['overall_average_sentiment'],
        mode='lines',
        name='Overall Sentiment',
        customdata=combined_sentiment_df['overall_label'],
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>Score:</b> %{y:.0f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'
    ))

    start_date_plot_os = combined_sentiment_df.index.max() - pd.DateOffset(years=1)
    fig_overall_sentiment.update_layout(
        dragmode='pan',
        title='Historical Market Sentiment',
        xaxis_title='', yaxis_title='Aggregate Sentiment Score',
        hovermode='x unified',
        # Set default X-axis view to the last 1 year
        xaxis_range=[start_date_plot_os, combined_sentiment_df.index.max()],
        # Set Y-range to 0-100
        yaxis_range=[0, 100],
        # Enable interval selector
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date"
        )
    )
    st.plotly_chart(fig_overall_sentiment, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})

# Setup tabs for different catagories of indicators
tab1, tab2, tab3 = st.tabs(["Market Trend", "Asset Allocation", "Options Activity"])

# ==========================================
# TAB 1: MARKET Trend
# ==========================================
with tab1:
    # --- S&P 500 Trend ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_SPY125MA.py]

    latest_spy = df_spy.iloc[-1]
    score_spy = latest_spy['Score']

    def get_spy_sentiment(s):
      if s >= 76:
          return st.success(f"**Extreme Greed**")
      elif s >= 56:
          return st.success(f"**Greed**")
      elif s >= 45:
          return st.info(f"**Neutral**")
      elif s >= 25:
          return st.error(f"**Fear**")
      else:
          return st.error(f"**Extreme Fear**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("S&P 500 Trend")
        get_spy_sentiment(score_spy)
        #st.metric("Score", f"{score_spy:.0f}/100")
        st.write("Computed based on the percentile deviation of the current SPY price from its 125-day Moving Average. This moving average reflects the ongoing medium-term trading momentum of the S&P 500. Markets trading above their trend tend to reflect confidence and risk-taking behavior. Vice versa, persistent moves below this level often signal growing caution and weakening investor conviction.")

    # [Plotly_SPY125MA.py]

    end_date_plot = df_spy.index.max()
    start_date_plot = end_date_plot - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask = (df_spy.index >= start_date_plot) & (df_spy.index <= end_date_plot)
    recent_data = df_spy.loc[mask]
    y_min = recent_data['Close'].min() * 0.95 # 5% buffer
    y_max = recent_data['Close'].max() * 1.05 # 5% buffer

    # Generate Plotly
    with col2:
        plot_spy = df_spy
        fig_spy = go.Figure()
        fig_spy.add_trace(go.Scatter(x=plot_spy.index, y=plot_spy['Close'], name='SPY',
                                     customdata=plot_spy['Sentiment'],
                                     hovertemplate='<b>Price (SPY):</b> %{y:.2f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'))
        fig_spy.add_trace(go.Scatter(x=plot_spy.index, y=plot_spy['125MA'], name='125MA',
                                     hovertemplate='<b>125MA:</b> %{y:.2f}<extra></extra>'))

        fig_spy.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='SPY vs 125-Day Moving Average',
            yaxis_title='Price',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_plot, end_date_plot],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[y_min, y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_spy, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


    # --- Volatilit (VIX) Trend ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_VIX.py]

    score_vix = 100 - vix_df['Percentile'].iloc[-1]

    def get_vix_sentiment(s):
      if s >= 95:
          return st.success(f"**Extreme Greed**")
      elif s >= 80:
          return st.success(f"**Greed**")
      elif s >= 20:
          return st.info(f"**Neutral**")
      elif s >= 5:
          return st.error(f"**Fear**")
      else:
          return st.error(f"**Extreme Fear**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("Volatility (VIX) Trend")
        get_vix_sentiment(score_vix)
        #st.metric("Score", f"{score_vix:.0f}/100")
        st.write("Computed based on the percentile deviation of the current VIX from its 50-day Moving Average. The CBOE Volatility Index (VIX) measures the S&P 500’s expected volatility in the next 30 days based on the trading activities of its options. However, looking at the VIX directly dilutes actual sentiments with institutional hedging. Therefore, relativity to its short-term movement helps smooth these noises.")

    # [Plotly_VIX.py]

    # Calculate date ranges for the default 1-year view
    end_date_vix = vix_df.index.max()
    start_date_vix = end_date_vix - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_vix = (vix_df.index >= start_date_vix) & (vix_df.index <= end_date_vix)
    recent_vix = vix_df.loc[mask_vix]
    vix_y_min = recent_vix['Close'].min() * 0.9 # 10% buffer
    vix_y_max = recent_vix['Close'].max() * 1.1 # 10% buffer

    # Generate Plotly
    with col2:
        fig_vix = go.Figure()
        fig_vix.add_trace(go.Scatter(x=vix_df.index, y=vix_df['Close'], name='VIX',
                                     customdata=vix_df['Sentiment'],
                                     hovertemplate='<b>VIX Close:</b> %{y:.2f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'))
        fig_vix.add_trace(go.Scatter(x=vix_df.index, y=vix_df['50MA'], name='50MA',
                                     hovertemplate='<b>50MA:</b> %{y:.2f}<extra></extra>'))

        fig_vix.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='VIX vs 50-Day Moving Average',
            yaxis_title='Index',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_vix, end_date_vix],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[vix_y_min, vix_y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_vix, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})

# ==========================================
# TAB 2: ASSET ALLOCATION
# ==========================================
with tab2:
    # --- Safe Haven Demand ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_SafeHavenDemand.py]

    latest_sh = sh_returns.iloc[-1]
    score_sh = latest_sh['Score']

    def get_sh_sentiment(sentiment):
        if sentiment <= 25:
          return st.error(f"**Extreme Fear**")
        elif sentiment <= 40:
          return st.error(f"**Fear**")
        elif sentiment <= 60:
          return st.info(f"**Neutral**")
        elif sentiment <= 75:
          return st.success(f"**Greed**")
        else:
          return st.success(f"**Extreme Greed**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("Safe Haven Demand")
        get_sh_sentiment(score_sh)
        #st.metric("Score", f"{score_sh:.0f}/100")
        st.write("Stocks and bonds historically have an inverse relationship due to risk-related factors that are directly tied to trading sentiments. A preference for stocks typically signals optimism about economic growth and earnings. A shift toward bonds often indicates rising uncertainty or risk aversion. Because capital flows often move ahead of price trends, this spread can reveal sentiment shifts early.")

    # [Plotly_SafeHavenDemand.py]

    # Calculate date ranges for the default 1-year view
    end_date_sh = sh_returns.index.max()
    start_date_sh = end_date_sh - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_sh = (sh_returns.index >= start_date_sh) & (sh_returns.index <= end_date_sh)
    recent_sh = sh_returns.loc[mask_sh]
    sh_y_min = recent_sh['Spread'].min() * 100 - 0.5 # 0.5% buffer
    sh_y_max = recent_sh['Spread'].max() * 100 + 0.5 # 0.5% buffer

    # Generate Plotly
    with col2:
        fig_sh = go.Figure()
        fig_sh.add_trace(go.Scatter(
            x=sh_returns.index,
            y=sh_returns['Spread'] * 100,
            mode='lines',
            name='Spread (SPY-IEF)',
            customdata=sh_returns['Sentiment'],
            hovertemplate='<b>Spread:</b> %{y:.2f}%<br><b>Sentiment:</b> %{customdata}<extra></extra>'
        ))

        # Zero Line (Reference) - no sentiment needed here
        fig_sh.add_trace(go.Scatter(
            x=[sh_returns.index.min(), sh_returns.index.max()],
            y=[0, 0],
            mode='lines',
            line=dict(color='red', dash='dash', width=1),
            name='Baseline (0%)',
            showlegend=True,
            hovertemplate='<b>Baseline:</b> %{y:.2f}%<extra></extra>'
        ))

        fig_sh.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='20-Day Yield Spread: SPY vs IEF',
            yaxis_title='Difference in 20-Day Yield (%)',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_sh, end_date_sh],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[sh_y_min, sh_y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_sh, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


    # --- Growth vs Value ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_IVWvsIVE.py]

    latest_gv = gv_dev.iloc[-1]

    def get_gv_sentiment(s):
      if s >= 90:
          return st.success(f"**Extreme Greed**")
      elif s >= 70:
          return st.success(f"**Greed**")
      elif s >= 40:
          return st.info(f"**Neutral**")
      elif s >= 20:
          return st.error(f"**Fear**")
      else:
          return st.error(f"**Extreme Fear**")

    # Title, Sentiment, and Description
    with col1:
        st.subheader("Growth vs Value")
        get_gv_sentiment(latest_gv['Score'])
        #st.metric("Score", f"{latest_gv['Score']:.0f}/100")
        st.write("Sector rotation is very common and a core strategy for institutional traders, involving large capital shifts between market areas to capitalize on changing economic cycles and environment. Favoritism in growth stocks often reflects confidence, liquidity, and tolerance for risk. Value stocks tend to outperform during more cautious or late-cycle environments. ")

    # --- Plotly_IVWvsIVE.py ---

    # Calculate date ranges for the default 1-year view
    end_date_gv = gv_dev.index.max()
    start_date_gv = end_date_gv - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_gv = (gv_dev.index >= start_date_gv) & (gv_dev.index <= end_date_gv)
    recent_gv = gv_dev.loc[mask_gv]
    gv_y_min = min(recent_gv['IVW_dev'].min(), recent_gv['IVE_dev'].min()) - 2.0  # 2% buffer
    gv_y_max = max(recent_gv['IVW_dev'].max(), recent_gv['IVE_dev'].max()) + 2.0  # 2% buffer

    # Generate Plotly
    with col2:
        fig_gv = go.Figure()
        fig_gv.add_trace(go.Scatter(x=gv_dev.index, y=gv_dev['IVW_dev'], name='Growth Stocks (IVW)',
                                    customdata=gv_dev['Sentiment'],
                                    hovertemplate='<b>IVW Dev:</b> %{y:.2f}%<br><b>Sentiment:</b> %{customdata}<extra></extra>'))
        fig_gv.add_trace(go.Scatter(x=gv_dev.index, y=gv_dev['IVE_dev'], name='Value Stocks (IVE)',
                                    hovertemplate='<b>IVE Dev:</b> %{y:.2f}%<extra></extra>'))

        fig_gv.update_layout(
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='Growth Stocks vs Value Stocks (Relative to SPY)',
            yaxis_title='Deviation from S&P 500 (%)',
            hovermode='x unified',
            # Set default X-axis view to the last 1 year
            xaxis_range=[start_date_gv, end_date_gv],
            # Set Y-range based on the 1-year slice calculated above
            yaxis_range=[gv_y_min, gv_y_max],
            # Enable interval selector
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )
        st.plotly_chart(fig_gv, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})

# ==========================================
# TAB 3: OPTIONS ACTIVITY
# ==========================================
with tab3:
    # --- Put/Call Sentiment ---

    col1, col2 = st.columns([1, 3])

    # [SentimentScore_PutCall_Ratio.py]

    spy = yf.Ticker('SPY')
    option_dates = spy.options[:14] # Set observation range to the nearest 14 expirations
    pcr_results = []

    # Unlike previsous indicators, yfinance does not provide retrospective data on options
    # Per-date loop for the all SPY options in the observation rage
    for date in option_dates:
      chain = spy.option_chain(date)

      # Access volume and openInterest directly from the calls and puts DataFrames
      v_put = chain.puts['volume'].sum()
      v_call = chain.calls['volume'].sum()
      oi_put = chain.puts['openInterest'].sum() # Corrected access
      oi_call = chain.calls['openInterest'].sum() # Corrected access

      # Calculate ratios with safety checks for division by zero
      v_ratio = v_put / v_call if v_call > 0 else 0
      oi_ratio = oi_put / oi_call if oi_call > 0 else 0

      pcr_results.append({'date': date, 'v_pcr': v_ratio, 'oi_pcr': oi_ratio})

    pcr_df = pd.DataFrame(pcr_results)
    # Simple logic for "Highest Sentiment" quadrant
    avg_v = pcr_df['v_pcr'].mean()
    avg_oi = pcr_df['oi_pcr'].mean()

    def get_pcr_sentiment(s):
      sentiment_label = "Neutral"
      if avg_v > 1.0 and avg_oi > 1.0:
        return st.error(f"**Capitulation**")
      elif avg_v < 1.0 and avg_oi < 1.0:
        return st.success(f"**Bullish Setup**")
      elif avg_v > 1.0 and avg_oi < 1.0:
        return st.info(f"**Tactical Hedging**")
      elif avg_v < 1.0 and avg_oi > 1.0:
        return st.info(f"**Short Covering**")

    # Title, Sentiment, PCR, and Description
    with col1:
        st.subheader("Put/Call Sentiment")
        get_pcr_sentiment(pcr_df)
        st.write("Avg Vol PCR:", f"{avg_v:.2f}")
        st.write("Avg OI PCR:", f"{avg_oi:.2f}")
        st.write("Put/Call Ratio measures the trading activity on Put relative to Call options. A ratio above 1 suggests bearish sentiment (more puts), while below 1 indicates bullishness (more calls). Furthermore, PCR can be divided into volume and open interest, which can be roughly interpreted as the immediate flow and existing commitment in Puts (Bearish) and Calls (Bullish), respectively.")

    # [Plotly_PutCall_Ratio.py]

    today_ts = pd.Timestamp(dt.now().date())
    pcr_df['DTE'] = (pd.to_datetime(pcr_df['date']) - today_ts).dt.days

    with col2:
        fig_pcr = go.Figure(data=[
            go.Bar(x=pcr_df['DTE'], y=pcr_df['v_pcr'], name='Volume PCR',
              hovertemplate='DTE: %{x}<br>Volume PCR: %{y:.2f}<extra></extra>'),
            go.Bar(x=pcr_df['DTE'], y=pcr_df['oi_pcr'], name='OI PCR',
              hovertemplate='DTE: %{x}<br>OI PCR: %{y:.2f}<extra></extra>')
        ])
        fig_pcr.update_layout(
            dragmode='pan', 
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            title='Put/Call Ratios (Nearest 14 Expirations)', 
            xaxis=dict(
                title='DTE',
                type='category', 
                tickvals=pcr_df.index, 
                ticktext=pcr_df['DTE']
                )
            )
        st.plotly_chart(fig_pcr, width='stretch', config={'displayModeBar': False, 'scrollZoom': False})


    # --- Skew Diagnostics ---
    col1, col2 = st.columns([1, 3])

    # [SentimentScore_VolatilitySkew.py]
    current_price = spy.history(period="1d")['Close'].iloc[-1]
    ATM_WIN, OTM_PCT = 0.01, 0.10 # 1% ATM window, +-10% OTM window
    skew_results = []

    # Per-date loop for the all SPY options in the nearest 14 expirations
    for expiry in spy.options[:14]:
        opt = spy.option_chain(expiry)

        calls, puts = opt.calls.copy(), opt.puts.copy()
        calls["type"], puts["type"] = "call", "put"

        # Indentify ATM and OTM options
        df_skew = pd.concat([calls, puts])
        df_skew = df_skew[df_skew["impliedVolatility"] > 0]
        df_skew["moneyness"] = df_skew["strike"] / current_price
        atm = df_skew[(df_skew["moneyness"] > 1 - ATM_WIN) & (df_skew["moneyness"] < 1 + ATM_WIN)]
        otm_calls = df_skew[(df_skew["type"] == "call") & (df_skew["moneyness"] > 1 + OTM_PCT)]
        otm_puts = df_skew[(df_skew["type"] == "put") & (df_skew["moneyness"] < 1 - OTM_PCT)]

        # Compute "Tail-skew", "Put Convexity", and "Call-FOMO"
        if not (atm.empty or otm_calls.empty or otm_puts.empty):
            m = {"tail": otm_puts["impliedVolatility"].mean() / otm_calls["impliedVolatility"].mean(),
                 "put_conv": otm_puts["impliedVolatility"].mean() / atm["impliedVolatility"].mean(),
                 "call_fomo": otm_calls["impliedVolatility"].mean() / atm["impliedVolatility"].mean()}
            skew_results.append(m)

    # Compute the average of "Tail-skew", "Put Convexity", and "Call-FOMO" across all expirations
    df_m = pd.DataFrame(skew_results)
    avg_tail, avg_conv, avg_fomo = df_m["tail"].mean(), df_m["put_conv"].mean(), df_m["call_fomo"].mean()
    ts_slope = df_m.iloc[-1]["tail"] - df_m.iloc[0]["tail"]

    # Diagnostic results based on average
    with col1:
        st.subheader("Skew Diagnostics")
        if avg_tail > 1.3: st.error("- Strong downside tail fear")
        elif avg_tail > 1.1: st.warning("- Moderate downside risk awareness")
        else: st.success("- Balanced tail risk")

        if avg_conv > 1.4: st.error("- Crash protection demand elevated")
        if avg_fomo > 1.2: st.warning("- Upside FOMO / squeeze risk")
        if ts_slope < -0.1: st.error("- Near-term fear dominant")
        if ts_slope > 0.2: st.warning("- Long-term risk feared")
        else: st.success("- Stable term-structure sentiment")
        st.write("Implied Volatility (IV) significantly impacts option premiums. IV positively correlates to the expectation that the underlying option ends up “in the money”. Therefore, the volatility skew curve is a direct visualization of supply and demand dynamics influenced by trader sentiments. ")

    # [Plotly_VolatilitySkew.py]

    with col2:
        current_p = spy.history(period="1d")['Close'].iloc[-1]
        expirations_skew = spy.options[:14]
        fig_skew = go.Figure()
        # Set default X-axis view to +-5% from current SPY price
        x_min, x_max = current_p * 0.95, current_p * 1.05
        all_ivs = []

        # Compute IV curves
        for i, exp_date in enumerate(expirations_skew):
            # Format time to Days to Expiration
            dte = (dt.strptime(exp_date, '%Y-%m-%d').date() - dt.now().date()).days
            opt = spy.option_chain(exp_date)
            # Smoothing for reasonable liquidity and remove zero IV values
            c, p = opt.calls[opt.calls['impliedVolatility'] > 0.001].copy(), opt.puts[opt.puts['impliedVolatility'] > 0.001].copy()

            # Color code calls and puts, lighter color = further expiration
            for df_opt, color_base, group in [(c, '0, 128, 0', 'Calls'), (p, '255, 0, 0', 'Puts')]:
                df_opt['smooth'] = df_opt['impliedVolatility'].rolling(window=5, min_periods=1, center=True).mean()
                alpha = 1.0 - (i / len(expirations_skew)) * 0.9
                fig_skew.add_trace(go.Scatter(x=df_opt['strike'], y=df_opt['smooth'] * 100, mode='lines',
                                         line=dict(color=f'rgba({color_base}, {alpha})', width=1), showlegend=False,
                                         hovertemplate=f'<b>{dte} DTE</b>: %{{y:.2f}}%<extra></extra>'))

                # Collect IV for axis scaling
                mask = (df_opt['strike'] >= x_min) & (df_opt['strike'] <= x_max)
                all_ivs.extend((df_opt.loc[mask, 'smooth'] * 100).tolist())

        # Set default Y-axis view to +-5% from ATM IV
        if all_ivs:
            ymin, ymax = min(all_ivs) * 0.95, max(all_ivs) * 1.05
        else:
            ymin, ymax = 0, 100

        # Center line for current SPY price
        fig_skew.add_vline(x=current_p, line_dash="dash", line_color="grey")
        fig_skew.update_layout(
            title=f"Volatility Skew (Current Price: {current_p:.2f})", 
            xaxis_title="Strikes", 
            yaxis_title="Implied Volatility (IV)", 
            xaxis_range=[x_min, x_max], 
            yaxis_range=[ymin, ymax], 
            height=600, 
            dragmode='pan',
            paper_bgcolor='#f9f9f9',
            plot_bgcolor='#f9f9f9',
            )
        st.plotly_chart(fig_skew, width='stretch', config={'displayModeBar': False})

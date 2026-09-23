import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_overall_chart(combined_sentiment_df):
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
    return fig_overall_sentiment


def build_spy_chart(df_spy):
    end_date_plot = df_spy.index.max()
    start_date_plot = end_date_plot - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask = (df_spy.index >= start_date_plot) & (df_spy.index <= end_date_plot)
    recent_data = df_spy.loc[mask]
    y_min = recent_data['Close'].min() * 0.95 # 5% buffer
    y_max = recent_data['Close'].max() * 1.05 # 5% buffer

    plot_spy = df_spy
    fig_spy = go.Figure()
    fig_spy.add_trace(go.Scatter(x=plot_spy.index, y=plot_spy['Close'], name='SPY',
                                 customdata=plot_spy['Sentiment'],
                                 hovertemplate='<b>Price (SPY):</b> %{y:.2f}<extra></extra>'))
    fig_spy.add_trace(go.Scatter(x=plot_spy.index, y=plot_spy['125MA'], name='125MA',
                                 hovertemplate='<b>125MA:</b> %{y:.2f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'))

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
    return fig_spy


def build_vix_chart(vix_df):
    end_date_vix = vix_df.index.max()
    start_date_vix = end_date_vix - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_vix = (vix_df.index >= start_date_vix) & (vix_df.index <= end_date_vix)
    recent_vix = vix_df.loc[mask_vix]
    vix_y_min = recent_vix['Close'].min() * 0.9 # 10% buffer
    vix_y_max = recent_vix['Close'].max() * 1.1 # 10% buffer

    fig_vix = go.Figure()
    fig_vix.add_trace(go.Scatter(x=vix_df.index, y=vix_df['Close'], name='VIX',
                                 customdata=vix_df['Sentiment'],
                                 hovertemplate='<b>VIX Close:</b> %{y:.2f}<extra></extra>'))
    fig_vix.add_trace(go.Scatter(x=vix_df.index, y=vix_df['50MA'], name='50MA',
                                 hovertemplate='<b>50MA:</b> %{y:.2f}<br><b>Sentiment:</b> %{customdata}<extra></extra>'))

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
    return fig_vix


def build_safe_haven_chart(sh_returns):
    end_date_sh = sh_returns.index.max()
    start_date_sh = end_date_sh - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_sh = (sh_returns.index >= start_date_sh) & (sh_returns.index <= end_date_sh)
    recent_sh = sh_returns.loc[mask_sh]
    sh_y_min = recent_sh['Spread'].min() * 100 - 0.5 # 0.5% buffer
    sh_y_max = recent_sh['Spread'].max() * 100 + 0.5 # 0.5% buffer

    fig_sh = go.Figure()
    fig_sh.add_trace(go.Scatter(
        x=sh_returns.index,
        y=sh_returns['Spread'] * 100,
        mode='lines',
        name='SPY-IEF',
        customdata=sh_returns['Sentiment'],
        hovertemplate='<b>Spread:</b> %{y:.2f}%<br><b>Sentiment:</b> %{customdata}<extra></extra>'
    ))

    # Zero Line (Reference) - no sentiment needed here
    fig_sh.add_trace(go.Scatter(
        x=[sh_returns.index.min(), sh_returns.index.max()],
        y=[0, 0],
        mode='lines',
        line=dict(color='red', dash='dash', width=1),
        name='Baseline',
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
    return fig_sh


def build_growth_value_chart(gv_dev):
    end_date_gv = gv_dev.index.max()
    start_date_gv = end_date_gv - pd.DateOffset(years=1)

    # Filter data for the last year to calculate Y-axis scaling
    mask_gv = (gv_dev.index >= start_date_gv) & (gv_dev.index <= end_date_gv)
    recent_gv = gv_dev.loc[mask_gv]
    gv_y_min = min(recent_gv['IVW_dev'].min(), recent_gv['IVE_dev'].min()) - 2.0  # 2% buffer
    gv_y_max = max(recent_gv['IVW_dev'].max(), recent_gv['IVE_dev'].max()) + 2.0  # 2% buffer

    fig_gv = go.Figure()
    fig_gv.add_trace(go.Scatter(x=gv_dev.index, y=gv_dev['IVW_dev'], name='IVW',
                                customdata=gv_dev['Sentiment'],
                                hovertemplate='<b>IVW Dev:</b> %{y:.2f}%<extra></extra>'))
    fig_gv.add_trace(go.Scatter(x=gv_dev.index, y=gv_dev['IVE_dev'], name='IVE',
                                hovertemplate='<b>IVE Dev:</b> %{y:.2f}%<br><b>Sentiment:</b> %{customdata}<extra></extra>'))

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
    return fig_gv


def analyze_standardized_correlation(combined_sentiment_df, df_spy):
    df = pd.concat([
        combined_sentiment_df[['overall_average_sentiment']],
        df_spy[['Close']]
    ], axis=1).dropna()

    df['sentiment_pct'] = df['overall_average_sentiment'].pct_change()
    df['spy_pct'] = df['Close'].pct_change()
    df.dropna(inplace=True)

    # Z-Score Standardization
    df['sentiment_z'] = (df['sentiment_pct'] - df['sentiment_pct'].mean()) / df['sentiment_pct'].std()
    df['spy_z'] = (df['spy_pct'] - df['spy_pct'].mean()) / df['spy_pct'].std()
    df['rolling_corr'] = df['sentiment_z'].rolling(window=60).corr(df['spy_z'])

    # --- Generate Plot ---
    # Subplot: isolates Z-Score and Correlation Analysis
    fig = make_subplots(
      rows=2, cols=1,
      shared_xaxes=True,
      vertical_spacing=0.1,
      subplot_titles=(
          f"Z-Scores of Daily % Changes", "60-Day Rolling Correlation of Standardized % Change"
      )
    )

    # Top Plot: Z-Score Comparison
    # Visualizes correlation during extreme scenarios
    fig.add_trace(go.Scatter(
        x=df.index, y=df['spy_z'],
        name="SPY",
        line=dict(color='#1f77b4', width=1),
        opacity=0.5
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['sentiment_z'],
        name="Sentiment",
        line=dict(color='#bd4043', width=1),
        opacity=0.5
    ), row=1, col=1)

    # Bottom Plot: Rolling Correlation
    fig.add_trace(go.Scatter(
        x=df.index, y=df['rolling_corr'],
        name="60D Roll. Corr.",
        fill='tozeroy',
        line=dict(color='#1f77b4')
    ), row=2, col=1)

    fig.update_layout(
        title_text="Market Sentiment Score vs. SPY Performance",
        yaxis_range=[-3, 3],
        height=750,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        dragmode='pan',
        paper_bgcolor='#f9f9f9',
        plot_bgcolor='#f9f9f9'
    )

    fig.update_yaxes(title_text="Standard Deviations (Z-Score)", row=1, col=1)
    fig.update_yaxes(title_text="Correlation Coefficient", range=[-1, 1], row=2, col=1)
    return fig


def plot_recovery_boxplot(combined_sentiment_df):
    df = combined_sentiment_df[['overall_average_sentiment']].copy()
    df.index = pd.to_datetime(df.index)

    EF_THRESHOLD, NEUTRAL_THRESHOLD = 25, 45 # Sentiment Score Threasholds
    is_extreme_fear = df['overall_average_sentiment'] < EF_THRESHOLD # Triggers counter when score < 25
    ef_entries = df.index[is_extreme_fear & (~is_extreme_fear.shift(1, fill_value=False))]

    durations = []
    for start_date in ef_entries:
        future_data = df.loc[start_date:]
        recovery_event = future_data[future_data['overall_average_sentiment'] >= NEUTRAL_THRESHOLD] # Count calendar days until score >= 45
        if not recovery_event.empty:
            durations.append((recovery_event.index[0] - start_date).days)

    if not durations:
        return None

    fig = go.Figure(go.Box(
        y = durations,
        name = "Days",
        boxpoints = 'all', # Show all underlying data points next to the box
        jitter = 0.5,      # Spread out points so they don't overlap
        pointpos = -1.8,   # Position of points relative to the box
        line = dict(color='#1f77b4'),
        hovertemplate = 'Days: %{y}<extra></extra>'
    ))

    # Update Layout to match Dashboard theme
    fig.update_layout(
        title={
            'text': "Distribution of Recovery Times: Extreme Fear to Neutral",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title="Calendar Days until Recovery",
        xaxis=dict(showticklabels=False),
        template="plotly_white",
        #width=1200,
        height=800,
        showlegend=False,
        dragmode='pan',
        paper_bgcolor='#f9f9f9',
        plot_bgcolor='#f9f9f9'
    )
    return fig


def plot_multi_horizon_performance(combined_sentiment_df, df_spy):

    data = pd.DataFrame(index=combined_sentiment_df.index)
    data['Label'] = combined_sentiment_df['overall_label']
    data['Price'] = df_spy['Close']
    data.dropna(subset=['Label', 'Price'], inplace=True)

    horizons = {'6-Month': 126, '12-Months': 252, '24-Months': 504, '36-Months': 756} # Trading day approximations

    for name, period in horizons.items():
        data[f'{name}_Ret'] = (data['Price'].shift(-period) / data['Price'] - 1) * 100

    label_order = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    performance_cols = [f'{name}_Ret' for name in horizons.keys()]

    long_df = data.melt(id_vars=['Label'], value_vars=performance_cols, var_name='Horizon_Ret_Col', value_name='Return')
    long_df['Horizon'] = long_df['Horizon_Ret_Col'].str.replace('_Ret', '')
    long_df['Label'] = pd.Categorical(long_df['Label'], categories=label_order, ordered=True)
    long_df.sort_values(by=['Label', 'Horizon'], inplace=True)

    fig = go.Figure()
    colors = ['#aec7e8', '#7fb3d5', '#2980b9', '#154360'] # Light to Dark Blue

    for i, horizon_name in enumerate(horizons.keys()):
        horizon_data = long_df[long_df['Horizon'] == horizon_name]
        fig.add_trace(go.Box(
            x=horizon_data['Label'],
            y=horizon_data['Return'],
            name=horizon_name,
            marker_color=colors[i],
            boxpoints='outliers',
            boxmean=True))

    fig.update_layout(
          title={
              'text': "Distribution of Forward Returns by Aggregate Sentiment Regime",
              'y': 0.95, 'x': 0.5, 'xanchor': 'center'
          },
          xaxis_title="Aggregate Sentiment",
          yaxis_title="Forward Return (%)",
          boxmode='group', # Groups the boxes for each sentiment label
          template="plotly_white",
          legend=dict(
              orientation="h",
              yanchor="bottom", y=1.02,
              xanchor="right", x=1
          ),
          height=600,
          dragmode='pan',
          paper_bgcolor='#f9f9f9',
          plot_bgcolor='#f9f9f9'
      )

    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
    return fig

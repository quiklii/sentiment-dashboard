# app/pages/main_page.py

import streamlit as st
import pandas as pd
import altair as alt

from src.visualizations.plots import create_main_chart, create_trend_chart, rating_distribution_chart
from src.analytics.aggregations import display_delta, calculate_delta

from src.utils.logger import get_logger
logger = get_logger(__name__)

# Mapping time scale to Altair time unit
timeunit_map = {
    'Daily': 'yearmonthdate',
    'Weekly': 'yearweek',
    'Monthly': 'yearmonth',
    'Quarterly': 'yearquarter',
    'Yearly': 'year'
}
           
# Custom sentiment progress bar (still dont know if its good)
def sentiment_progress_bar(value: float, height: int = 10):
    """
    Custom progress bar with dynamic color (red → yellow → green).
    Always fills container width.
    Args:
        value: float 0–100
        height: thickness of the bar in px
    """
    value = max(0, min(100, float(value)))

    # compute gradient color dynamically
    # 0→50 red→yellow , 50→100 yellow→green
    if value <= 50:
        # red → yellow
        r = 255
        g = int(255 * (value / 50))
        b = 0
    else:
        # yellow → green
        r = int(255 * (1 - (value - 50) / 50))
        g = 255
        b = 0

    color = f"rgb({r},{g},{b})"

    bar_html = f"""
    <div style="
        width: 100%;
        background-color: rgba(200,200,200,0.15);
        border-radius: {height}px;
        height: {height}px;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            width: {value}%;
            background-color: {color};
            height: 100%;
            border-radius: {height}px;
            transition: width 0.4s ease, background-color 0.4s ease;
        "></div>
    </div>
    """

    st.markdown(bar_html, unsafe_allow_html=True)

# KPI cards
def kpi_cards(df: pd.DataFrame, df_filtered: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "cum_reviews")
            st.metric("💬 Review count",
                      f'{df["cum_reviews"].iloc[-1]:,}', delta=0.0)

    with col2:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "avg_rating")
            st.metric(
                "⭐ Rating average",
                f'{df["avg_rating"].iloc[-1]:.2f} / 5.0',
                delta=display_delta(delta),
            )
            st.altair_chart(rating_distribution_chart(df_filtered), width='stretch')

    with col3:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "sentiment_index")
            st.metric(
                "📊 Sentiment Index",
                f'{df["sentiment_index"].iloc[-1]:.2f} / 100',
                delta=display_delta(delta),
            )
            sentiment_progress_bar(df["sentiment_index"].iloc[-1])

    with col4:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "positive_ratio")
            st.metric(
                "😃 Positive",
                f'{df["positive_ratio"].iloc[-1]:.0%}',
                delta=display_delta(delta, decimals=2,
                                    scale=100, suffix="p.p."),
            )
            neg = df["negative_ratio"].iloc[-1]
            neu = df["neutral_ratio"].iloc[-1]
            st.caption(f"Negative: {neg:.0%} | Neutral: {neu:.0%}")


# --- MAIN PAGE ---
st.title('Main page')
st.write('Welcome to Sentience Dashboard. This is an overview of your sentiment analysis data.')

try:
    df_filtered = st.session_state['df_filtered']
    df_display = st.session_state['df_display']

    if df_display.empty:
        st.warning('No data available to display.')
    else:
        # kpi
        kpi_cards(df_display, df_filtered)
        
        # Controls in one row
        col_controls1, col_controls2 = st.columns(2)
        
        with col_controls1:
            color = st.toggle(
                'Color',
                value=True,
                key='main_chart_color',
                help='Toggle to enable/disable color coding by sentiment.'
            )
        
        with col_controls2:
            chart2_type = st.selectbox(
                'Select Trend Chart Type',
                options=['Sentiment Ratio', 'Sentiment Index', 'Average Rating'],
                key='trend_chart_type',
                label_visibility='collapsed',
                width=250
            )
        
        chart_type_map = {
            'Sentiment Ratio': 'sentiment_proportion',
            'Sentiment Index': 'sentiment_index',
            'Average Rating': 'avg_rating'
        }
        
        # charts in different row
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            chart1 = create_main_chart(
                df_display, timeunit_map[st.session_state['timescale']], color, height=450
            )
            st.altair_chart(chart1, width='stretch')
        
        with col_chart2:
            chart2 = create_trend_chart(
                df_display,
                timeunit_map[st.session_state['timescale']],
                chart_type=chart_type_map[chart2_type],
                height=450
            )
            st.altair_chart(chart2, width='stretch')
        #st.dataframe(df_filtered.head(10))
                
except Exception as e:
    logger.error(f"Error loading data", exc_info=True)
    st.error(f'An error occurred while loading the data: {e}')
    st.exception(e)

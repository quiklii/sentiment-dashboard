# app/pages/main_page.py

import streamlit as st
import pandas as pd

from src.common.cache import get_data

from src.utils.logger import get_logger
logger = get_logger(__name__)


def display_delta(delta, decimals=2, scale=1.0, suffix=''):
    if delta is None:
        return None
    value = delta * scale
    if round(value, decimals) == 0:
        return None
    return f"{value:.{decimals}f}{suffix}" if suffix else round(value, decimals)


def calculate_delta(df: pd.DataFrame, column: str) -> float | None:
    df = df.dropna(subset=[column]).copy()
    if len(df) < 2:
        return 0
    delta = df[column].iloc[-1] - df[column].iloc[-2]
    return delta

# KPI cards


def kpi_cards(df: pd.DataFrame):
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

    with col3:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "sentiment_index")
            st.metric(
                "📊 Sentiment Index",
                f'{df["sentiment_index"].iloc[-1]:.2f} / 100',
                delta=display_delta(delta),
            )

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
        kpi_cards(df_display)
except Exception as e:
    logger.error(f"Error loading data", exc_info=True)
    st.error(f'An error occurred while loading the data: {e}')
    st.exception(e)

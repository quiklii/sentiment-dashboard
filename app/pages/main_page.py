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

# --- MAIN PAGE ---
st.title('Main page')
st.write('Welcome to Sentience Dashboard. This is an overview of your sentiment analysis data.')

try:
    df = get_data()
    
    if df.empty:
        st.warning('No data available to display.')
    else:
        with st.sidebar:
            st.header('Overview Metrics')
except Exception as e:
    logger.error(f"Error loading data", exc_info=True)
    st.error(f'An error occurred while loading the data: {e}')
    st.exception(e)
# app/Main.py
import streamlit as st
import pandas as pd
from pathlib import Path

from src.common.cache import get_data
from src.analytics.aggregations import aggregate_by_timeframe
from src.utils.logger import get_logger

logger = get_logger(__name__)

# --- CONFIG ---
st.set_page_config(
    page_title='Sentience Dashboard',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# --- PAGE SETUP ---
main_page = st.Page(
    page='pages/main_page.py',
    title='Main Page',
    icon=':material/home:',
    default=True
)
content_page = st.Page(
    page='pages/content_analysis.py',
    title='Content Analysis',
    icon=':material/article:',
)
strategy_page = st.Page(
    page='pages/strategy_navigator.py',
    title='Strategy Navigator',
    icon=':material/explore:',
)

# --- NAVIGATION SETUP ---
pg = st.navigation(pages=[main_page, content_page,
                   strategy_page], position='top')


# --- GET DATA ---
df = get_data()

# --- SIDEBAR SETUP ---
with st.sidebar:
    st.header('Overview Metrics')
    # Location filter
    locations = df['place_name'].unique().tolist()
    selected_locations = st.multiselect(
        'Select Locations', options=locations, default=locations)
    if selected_locations == []:
        df_filter_loc = df.copy()
    else:
        df_filter_loc = df[df['place_name'].isin(selected_locations)].copy()

    # Date input
    max_date = df_filter_loc["publish_time"].max().date()
    min_date = df_filter_loc["publish_time"].min().date()

    if (max_date - min_date).days > 365:
        default_start_date = max_date - pd.Timedelta(days=365)
    else:
        default_start_date = min_date

    default_end_date = max_date

    date_range = st.date_input(
        "Choose timeframe:",
        value=(default_start_date, default_end_date),
        min_value=min_date,
        max_value=max_date,
    )
    
    # Wait for both dates to be selected
    if len(date_range) != 2:
        st.warning("Please select both start and end dates.")
        st.stop()
    
    start_date, end_date = date_range
    df_filtered = df_filter_loc[
        (df_filter_loc["publish_time"].dt.date >= start_date)
        & (df_filter_loc["publish_time"].dt.date <= end_date)
    ].copy()

    # Time scale selection
    options = ['Daily', 'Weekly']
    if end_date - start_date > pd.Timedelta(days=30):
        options = options + ['Monthly']
    if end_date - start_date > pd.Timedelta(days=90):
        options = options + ['Quarterly']
    if end_date - start_date > pd.Timedelta(days=365):
        options = options + ['Yearly']
    timescale = st.selectbox('Select Time Scale', options=options)

    timescale_map = {
        'Daily': 'D',
        'Weekly': 'W-MON',
        'Monthly': 'M',
        'Quarterly': 'Q',
        'Yearly': 'Y'
    }
    df_display = aggregate_by_timeframe(df_filtered, timescale_map[timescale])

# --- SESSION STATE SETUP ---
# Always update session state with latest filtered data
st.session_state['df_filtered'] = df_filtered
st.session_state['df_display'] = df_display
st.session_state['timescale'] = timescale

# --- RUN NAVIATION ---
pg.run()

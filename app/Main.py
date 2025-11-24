# app/Main.py
import streamlit as st
import pandas as pd
from pathlib import Path

from src.data_loader import load_enriched_data
from src.utils.logger import get_logger

logger = get_logger(__name__)

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
pg = st.navigation(pages=[main_page, content_page, strategy_page], position='top')

# --- RUN NAVIATION ---
pg.run()

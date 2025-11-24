# src/common/cache.py

import streamlit as st
import pandas as pd
from pathlib import Path

from src.data_loader import load_enriched_data
from src.utils.logger import get_logger

logger = get_logger(__name__)

# File path
PROJECT_ROOT = Path(__file__).resolve().parents[2] # resolve() - get absolute path, parent[2] - go up two levels to 'src'
DATA_FILE_PATH = PROJECT_ROOT / 'src' / 'data' / 'reviews.csv'

@st.cache_data(show_spinner="Loading data...")
def get_data(file_path: Path = DATA_FILE_PATH) -> pd.DataFrame:
    """Load and cache enriched data from the specified file path."""
    df = load_enriched_data(file_path)
    logger.info(f"Data loaded to cache with {len(df)} records.")
    return df
# src/common/cache.py

import streamlit as st
import pandas as pd
from pathlib import Path

from src.data_loader import load_enriched_data
from src.utils.logger import get_logger
from src.analytics.aggregations import aggregate_by_timeframe, ngram_distribution

logger = get_logger(__name__)

# File path
PROJECT_ROOT = Path(__file__).resolve().parents[2] # resolve() - get absolute path, parent[2] - go up two levels to 'src'
DATA_FILE_PATH = PROJECT_ROOT / 'src' / 'data' / 'reviews.csv'

@st.cache_data(show_spinner="Loading data...", show_time=True)
def get_data(file_path: Path = DATA_FILE_PATH) -> pd.DataFrame:
    """Load and cache enriched data from the specified file path."""
    
    df = load_enriched_data(file_path)
    logger.info(f"Data loaded to cache with {len(df)} records.")
    return df

@st.cache_data(show_spinner="Aggregating data...")
def get_aggregated_data(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Aggregate data by the specified timeframe frequency."""
    
    aggregated_df = aggregate_by_timeframe(df, freq)
    logger.info(f"Aggregated data cached with frequency '{freq}' and {len(aggregated_df)} records.")
    return aggregated_df

@st.cache_data(show_spinner="Loading n-gram distributions...")
def get_ngram_distributions(df: pd.DataFrame) -> dict:
    """Calculate and cache n-gram distributions from the tokenized texts."""
    
    ngram_dists = ngram_distribution(df)
    logger.info("N-gram distributions cached.")
    return ngram_dists
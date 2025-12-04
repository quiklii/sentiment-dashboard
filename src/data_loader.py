import pandas as pd

from src.preprocess import format_data, clean_data, tokenize_texts
from src.sentiment_analysis import analyze_sentiments
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_data(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file into a pandas DataFrame."""
    logger.info(f'Loading raw data from: {file_path}...')

    try:
        data = pd.read_csv(file_path)
        logger.info(f'Raw data loaded successfully with shape: {data.shape}')
        return data
    except Exception as e:
        logger.error(f'Error loading raw data', exc_info=True)
        return pd.DataFrame()


def load_enriched_data(file_path: str) -> pd.DataFrame:
    """Load enriched data"""
    logger.info(f'Loading enriched data from: {file_path}...')
    df = load_data(file_path)
    if df.empty:
        logger.warning('Data is empty')
        return df
    df = format_data(df)
    df_analyzed = analyze_sentiments(clean_data(df))
    df_nlp = tokenize_texts(clean_data(df))
    df = pd.merge(df, df_nlp, on='review_id', how='left')

    return pd.merge(df, df_analyzed, on='review_id', how='left')

# src/preprocess.py

import pandas as pd

from src.nlp.preprocess import preprocess_text

from src.utils.logger import get_logger
logger = get_logger(__name__)

def format_data(df: pd.DataFrame) -> pd.DataFrame:
    """Perform basic data formatting on the DataFrame."""
    
    logger.info('Starting data formatting process...')
    if df.empty:
        logger.warning('Input DataFrame is empty')
        return df
    df = df.drop_duplicates().copy()
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
    df['reply_publish_time'] = pd.to_datetime(df['reply_publish_time'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    logger.info('Data formatting process completed')
    
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the dataframe for sentiment analysis and natural language processing."""
    
    logger.info('Starting data cleaning process...')
    if df.empty:
        logger.warning('Input DataFrame is empty')
        return df
    logger.debug(f'Initial DataFrame shape: {df.shape}')
    df = df.dropna(subset=['review_text']).copy()
    df = df[df['review_text'].str.strip() != '']
    df['review_text'] = df['review_text'].apply(lambda x: ' '.join(x.split()))
    logger.debug(f'Cleaned DataFrame shape: {df.shape}')
    logger.info('Data cleaning process completed')
    
    return df

def tokenize_texts(df: pd.DataFrame) -> pd.DataFrame:
    """Tokenize and preprocess the 'review_text' column using SpaCy."""
    
    logger.info('Starting text tokenization...')
    if df.empty:
        logger.warning('Input DataFrame is empty')
        return df
    df = df.copy()
    df['clean_tokens'] = df['review_text'].apply(lambda x: preprocess_text(x)['clean_tokens']).apply(tuple)
    logger.info('Text tokenization completed')
    return df[['review_id', 'clean_tokens']]   
    
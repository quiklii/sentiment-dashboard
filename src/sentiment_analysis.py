# src/sentiment_analysis.py

import pandas as pd
from transformers import pipeline

from src.utils.logger import get_logger
logger = get_logger(__name__)

def analyze_sentiments(df: pd.DataFrame) -> pd.DataFrame:
    """Perform sentiment analysis on the 'review_text' column of the DataFrame."""
    df = df.copy()
    
    logger.info('Starting sentiment analysis process')
    if df.empty:
        logger.warning('Input DataFrame is empty')
        return df
    logger.debug(f'Fetching model...')
    classifier = pipeline('sentiment-analysis', model='quikli/sentience-sentiment_analysis')
    results = classifier(df['review_text'].tolist())
    
    df['sentiment_label'] = [res['label'] for res in results]
    df['sentiment_score'] = [res['score'] for res in results]
    df['weighted_sentiment'] = df['sentiment_score'] * df['rating']
    
    logger.info('Sentiment analysis process completed')
    
    return df
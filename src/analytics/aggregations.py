# src/analytics/aggregations.py

import pandas as pd

from collections import Counter

from src.nlp.preprocess import extract_ngrams

from src.utils.logger import get_logger
logger = get_logger(__name__)


def aggregate_by_timeframe(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Aggregate data by the specified timeframe frequency."""
    
    logger.info(f"Aggregating data with frequency: {freq}")
    df = df.copy()

    if df.index.name != 'publish_time':
        df = df.set_index('publish_time')
    df['n_reviews'] = 1

    # one_hot = (
    #     pd.get_dummies(df['sentiment_label'])
    #     .reindex(columns=['Positive', 'Neutral', 'Negative'], fill_value=0)
    # )
    # df = pd.concat([df, one_hot], axis=1)
    df['n_analyzed'] = df['review_text'].notnull().astype(int)

    agg_dict = {
        'n_reviews': 'sum',
        'n_analyzed': 'sum',
        'rating': 'sum',
        'Positive': 'sum',
        'Neutral': 'sum',
        'Negative': 'sum',
        'sentiment_score': 'sum',
        'weighted_sentiment': 'sum'
    }

    # --- RESAMPLE AND AGGREGATE ---
    df_resampled = df.resample(freq).agg(agg_dict)

    df_resampled[['cum_positive', 'cum_neutral', 'cum_negative', 'cum_reviews', 'cum_analyzed', 'cum_weighted_sentiment', 'cum_sentiment_score', 'cum_rating']] = \
        df_resampled[['Positive', 'Neutral', 'Negative', 'n_reviews', 'n_analyzed',
                      'weighted_sentiment', 'sentiment_score', 'rating']].cumsum()

    df_resampled['avg_rating'] = df_resampled['cum_rating'] / \
        df_resampled['cum_reviews'].replace(0, pd.NA)

    for label in ['positive', 'neutral', 'negative']:
        df_resampled[f'{label}_ratio'] = df_resampled[f'cum_{label}'] / \
            df_resampled['cum_analyzed'].replace(0, pd.NA)
    df_resampled['sentiment_index'] = (
        df_resampled['cum_weighted_sentiment'] / df_resampled['cum_sentiment_score'].replace(0, pd.NA) + 1) * 50

    logger.info(
        f"Aggregation complete. Resulting data has {len(df_resampled)} records.")
    
    df_resampled = df_resampled.reset_index()
    
    # Offset (-1) publish_time for weekly aggregation to represent the week correctly
    # It is needed for proper W-MON display in Altair charts since Vega treats weeks starting on Sunday
    if freq == 'W-MON':
        df_resampled['publish_time'] = df_resampled['publish_time'] - pd.Timedelta(days=1)

    return df_resampled

def ngram_distribution(df: pd.DataFrame) -> dict:
    """Calculate n-gram distribution from the tokenized texts."""
    logger.info("Calculating n-gram distribution...")
    results = {}
    df = df[df['clean_tokens'].notnull()].copy()
    for n in range(1, 4):
        ngram_series = df['clean_tokens'].apply(lambda x: extract_ngrams(x, n))
        all_ngrams = [ngram for row in ngram_series for ngram in row]
        counts = Counter(all_ngrams)
        
        ngrams_counts = {'ngram': list(counts.keys()), 'count': list(counts.values())}
        
        # df_counts = (
        #     pd.DataFrame(counts.items(), columns=['ngram', 'count'])
        #     .sort_values('count', ascending=False)
        #     .reset_index(drop=True)
        # )
        results[f'{n}_gram'] = ngrams_counts
        logger.info(f"Calculated {len(ngrams_counts['ngram'])} unique {n}-grams.")
    return results

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
        
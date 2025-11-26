# src/analytics/aggregations.py

import pandas as pd

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

    # # --- ADD LABELS ---
    # idx = df_resampled.index

    # if freq == 'D':
    #     labels = idx.strftime('%Y-%m-%d')

    # elif freq == 'W-MON':
    #     iso = idx.isocalendar()
    #     labels = 'W' + iso.week.astype(str) + ' ' + iso.year.astype(str)

    # elif freq == 'M':
    #     labels = 'M' + idx.month.astype(str) + ' ' + idx.year.astype(str)

    # elif freq == 'Q':
    #     labels = 'Q' + idx.quarter.astype(str) + ' ' + idx.year.astype(str)

    # elif freq == 'Y':
    #     labels = idx.year.astype(str)

    # df_resampled['time_label'] = labels

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

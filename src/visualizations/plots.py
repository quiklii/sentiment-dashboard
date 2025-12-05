# src/visualizations/plots.py

import altair as alt
import pandas as pd

# --- MAIN PAGE CHARTS ---
# Chart 1 - per period
def create_main_chart(df: pd.DataFrame, time_unit: str, color: str, height: int = 400):
    
    if color:
        df_melt = df.melt(
            id_vars=['publish_time'],
            value_vars=['Positive', 'Neutral', 'Negative'],
            var_name='sentiment',
            value_name='count'
        )
    
        chart = alt.Chart(df_melt).mark_bar().encode(
            x=alt.X(
                f'{time_unit}(publish_time):O',
                title='Date',
                axis=alt.Axis(labelAngle=-45)
            ),
            y=alt.Y(
                'sum(count):Q',
                title='Count'
            ),
            color=alt.Color(
                'sentiment:N',
                scale=alt.Scale(
                    domain=['Positive', 'Neutral', 'Negative'],
                    range=['#22c55e', '#94a3b8', '#ef4444']
                ),
                legend=alt.Legend(title='Sentiment')
                ),
                order=alt.Order('sentiment:N', sort='descending'),
                tooltip=[
                    alt.Tooltip(f'{time_unit}(publish_time):O', title='Period'),
                    alt.Tooltip('sentiment:N', title='Sentiment'),
                    alt.Tooltip('sum(count):Q', title='Count', format=',')
                ]
        )
    else:
        df_chart = df[['publish_time', 'Positive', 'Neutral', 'Negative']].copy()
        df_chart['Total']= df_chart[['Positive', 'Neutral', 'Negative']].sum(axis=1)
        df_chart = df_chart[['publish_time', 'Total']]
        
        chart = alt.Chart(df_chart).mark_bar(color='lightgray').encode(
            x=alt.X(
                f'{time_unit}(publish_time):O',
                title='Date',
                axis=alt.Axis(labelAngle=-45)
            ),
            y=alt.Y(
                'sum(Total):Q',
                title='Count'
            ),
            tooltip=[
                alt.Tooltip(f'{time_unit}(publish_time):O', title='Period'),
                alt.Tooltip('sum(Total):Q', title='Count', format=',')
            ]
        )
        
    return chart.properties(height=height)

# Chart 2 - trend over time (multiple options)
def create_trend_chart(df: pd.DataFrame, time_unit: str, chart_type: str, height: int = 400):
    """
    Create trend chart with multiple visualization options.
    
    chart_type options:
    - 'sentiment_index': Line chart of Sentiment Index
    - 'avg_rating': Line chart of Average Rating  
    - 'sentiment_proportion': Normalized stacked area chart of sentiment proportions
    """
    
    # Config
    config = {
        'sentiment_index': {'title': 'Sentiment Index', 'color': 'lightgreen'},
        'avg_rating': {'title': 'Average Rating', 'color': 'gold'}
    }
    
    x_enc = alt.X(f'{time_unit}(publish_time):O', title='Date', axis=alt.Axis(labelAngle=-45))
    
    if chart_type == 'sentiment_proportion':
        df = df.melt(
            id_vars=['publish_time'],
            value_vars=['positive_ratio', 'neutral_ratio', 'negative_ratio'],
            var_name='sentiment',
            value_name='proportion'
        )
        chart = alt.Chart(df).mark_area().encode(
            x=x_enc,
            y=alt.Y('proportion:Q', stack='normalize', title='Proportion', axis=alt.Axis(format='%')),
            color=alt.Color('sentiment:N',
                scale=alt.Scale(
                    domain=['positive_ratio', 'neutral_ratio', 'negative_ratio'],
                    range = ['#22c55e', '#94a3b8', '#ef4444']
                ),
                legend=alt.Legend(title='Sentiment')
            ),
            order=alt.Order('sentiment:N', sort='descending'),
            tooltip=[
                alt.Tooltip(f'{time_unit}(publish_time):O', title='Period'),
                alt.Tooltip('sentiment:N', title='Sentiment'),
                alt.Tooltip('proportion:Q', title='Proportion', format='.1%')
            ]
        )
    else:
        c = config[chart_type]
        df = df[['publish_time', chart_type]].copy()
        
        chart = alt.Chart(df).mark_area(
            line={'color' : c['color']},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='white', offset=0),
                       alt.GradientStop(color=c['color'], offset=1)],
                x1=1, y1=1, x2=1, y2=0
            )
        ).encode(
            x=x_enc,
            y=alt.Y(f'{chart_type}:Q', title=c['title']),
            tooltip=[
                alt.Tooltip(f'{time_unit}(publish_time):O', title='Period'),
                alt.Tooltip(f'{chart_type}:N', title=c['title'], format='.2f')
            ]
        )
    
    return chart.properties(height=height)

# Rating distribution chart
def rating_distribution_chart(df: pd.DataFrame, height: int = 65):

    dist = (
        df['rating']
        .value_counts()
        .reindex([5, 4, 3, 2, 1], fill_value=0)
        .reset_index()
    )
    dist.columns = ['rating', 'count']

    chart = (
        alt.Chart(dist)
        .mark_bar(size=15, cornerRadius=5, color='#d4af37')
        .encode(
            x=alt.X(
                'rating:O',
                sort=[5, 4, 3, 2, 1],
                axis=alt.Axis(labelAngle=0, title=None, labelPadding=4)
            ),
            y=alt.Y(
                'count:Q',
                title=None,
                axis=alt.Axis(labels=False, ticks=False, domain=False)  # deletes y-axis
            ),
            tooltip=['rating','count']
        )
        .properties(
            height=height,
            padding={'left': 0, 'right': 0, 'top': 0, 'bottom': -1}
        )
    )

    return chart

# --- CONTENT ANALYSIS CHARTS ---
# N-gram bar chart
def ngram_bar_chart(ngram_dist: dict, color: str, top_n: int = 20, height: int = 500):
    """Create a bar chart for n-gram distribution."""
    df_ngrams = pd.DataFrame({
        'ngram': ngram_dist['ngram'],
        'count': ngram_dist['count']
    })
    df_ngrams['ngram'] = df_ngrams['ngram'].apply(
        lambda x: ' '.join(x) if isinstance(x, tuple) else x
    )
    df_ngrams = df_ngrams.head(top_n)
    
    chart = alt.Chart(df_ngrams).mark_bar(color=color).encode(
        x=alt.X('count:Q', title='Count'),
        y=alt.Y('ngram:N', 
                sort='-x', 
                title=None,
                axis=alt.Axis(
                    labelLimit=1000,
                    labelOverlap=False
                )
        ),
        tooltip=[
            alt.Tooltip('ngram:N', title='N-gram'),
            alt.Tooltip('count:Q', title='Count')
        ]
    ).properties(height=height)

    return chart
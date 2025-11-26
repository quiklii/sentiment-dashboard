# app/pages/main_page.py

import streamlit as st
import pandas as pd
import altair as alt

from src.common.cache import get_data

from src.utils.logger import get_logger
logger = get_logger(__name__)

# Mapping time scale to Altair time unit
timeunit_map = {
    'Daily': 'yearmonthdate',
    'Weekly': 'yearweek',
    'Monthly': 'yearmonth',
    'Quarterly': 'yearquarter',
    'Yearly': 'year'
}

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

# Chart 1 - per period
def create_main_chart(df: pd.DataFrame, time_unit: str, height: int = 400):
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
    ).properties(
        height=height
    )
    
    return chart

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
            #order=alt.Order('sentiment:N', sort='descending'),
            tooltip=[
                alt.Tooltip(f'{time_unit}(publish_time):O', title='Period'),
                alt.Tooltip('sentiment:N', title='Sentiment'),
                alt.Tooltip('proportion:Q', title='Proportion', format='.1%')
            ]
        )
    else:
        c = config[chart_type]
        
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
            


# KPI cards
def kpi_cards(df: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "cum_reviews")
            st.metric("💬 Review count",
                      f'{df["cum_reviews"].iloc[-1]:,}', delta=0.0)

    with col2:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "avg_rating")
            st.metric(
                "⭐ Rating average",
                f'{df["avg_rating"].iloc[-1]:.2f} / 5.0',
                delta=display_delta(delta),
            )

    with col3:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "sentiment_index")
            st.metric(
                "📊 Sentiment Index",
                f'{df["sentiment_index"].iloc[-1]:.2f} / 100',
                delta=display_delta(delta),
            )

    with col4:
        with st.container(border=True, height="stretch"):
            delta = calculate_delta(df, "positive_ratio")
            st.metric(
                "😃 Positive",
                f'{df["positive_ratio"].iloc[-1]:.0%}',
                delta=display_delta(delta, decimals=2,
                                    scale=100, suffix="p.p."),
            )
            neg = df["negative_ratio"].iloc[-1]
            neu = df["neutral_ratio"].iloc[-1]
            st.caption(f"Negative: {neg:.0%} | Neutral: {neu:.0%}")


# --- MAIN PAGE ---
st.title('Main page')
st.write('Welcome to Sentience Dashboard. This is an overview of your sentiment analysis data.')

try:
    df_filtered = st.session_state['df_filtered']
    df_display = st.session_state['df_display']

    if df_display.empty:
        st.warning('No data available to display.')
    else:
        # kpi
        kpi_cards(df_display)
        
        # chart 1 + chart 2
        col_chart1, col_chart2 = st.columns(2)
        with st.container():
            with col_chart1:
                chart1_type = st.selectbox(
                    'Select Main Chart Type',
                    options=['Sentiment Counts'],
                    key='main_chart_type',
                    width=200,
                    label_visibility='hidden'
                )
                chart1 = create_main_chart(
                    df_display, timeunit_map[st.session_state['timescale']], height=400)
                st.altair_chart(chart1, width='stretch')
            with col_chart2:
                chart2_type = st.selectbox(
                    'Select Trend Chart Type',
                    options=['Sentiment Ratio', 'Sentiment Index', 'Average Rating'],
                    key='trend_chart_type',
                    width=200,
                    label_visibility='hidden'
                )
                chart_type_map = {
                    'Sentiment Ratio': 'sentiment_proportion',
                    'Sentiment Index': 'sentiment_index',
                    'Average Rating': 'avg_rating'
                }
                chart2 = create_trend_chart(
                    df_display,
                    timeunit_map[st.session_state['timescale']],
                    chart_type=chart_type_map[chart2_type],
                    height=400
                )
                st.altair_chart(chart2, width='stretch')
                
except Exception as e:
    logger.error(f"Error loading data", exc_info=True)
    st.error(f'An error occurred while loading the data: {e}')
    st.exception(e)

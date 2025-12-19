# app/pages/content_analysis.py

import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from src.analytics.aggregations import evidence_search

from src.visualizations.wordcloud import generate_wordcloud, render_wordcloud_figure
from src.visualizations.plots import ngram_bar_chart, render_pie_chart

from src.utils.logger import get_logger
logger = get_logger(__name__)

# st.title('Content Analysis')

# # --- CONTENT ANALYSIS PAGE ---
# with st.container():
#     options = {'Unigram': '1', 'Bigram': '2', 'Trigram': '3'}
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader('Positive Reviews n-grams')
#         inner_cols = st.columns(4)
#         with inner_cols[0]:
#             ngram_type = st.selectbox(
#                 'Select n-gram type for Positive Reviews', 
#                 options=list(options.keys()), 
#                 key='pos_ngram_type', 
#                 width=150, 
#                 label_visibility='collapsed')
#         with inner_cols[1]:
#             toggle = st.toggle('Chart / Cloud', 
#                                value=True, 
#                                key='pos_ngram_toggle', 
#                                help='Toggle between Bar Chart and Word Cloud view for Positive Reviews n-grams.')
#         pos_ngrams_dists = st.session_state['positive_ngrams_dists']
#         if toggle:
#             wordcloud = generate_wordcloud(pos_ngrams_dists[f'{options[ngram_type]}_gram'], colormap='summer')
#             fig = render_wordcloud_figure(wordcloud)
#             st.pyplot(fig)
#         else:
#             chart = ngram_bar_chart(pos_ngrams_dists[f'{options[ngram_type]}_gram'], color='green')
#             st.altair_chart(chart, width='stretch')
#     with col2:
#         st.subheader('Negative Reviews n-grams')
#         inner_cols = st.columns(4)
#         with inner_cols[0]:
#             ngram_type = st.selectbox(
#                 'Select n-gram type for Negative Reviews', 
#                 options=list(options.keys()), 
#                 key='neg_ngram_type', 
#                 width=120, 
#                 label_visibility='collapsed')
#         with inner_cols[1]:
#             toggle = st.toggle('Chart / Cloud', 
#                                value=True, 
#                                key='neg_ngram_toggle', 
#                                help='Toggle between Bar Chart and Word Cloud view for Negative Reviews n-grams.')
#         neg_ngrams_dists = st.session_state['negative_ngrams_dists']
#         if toggle:
#             wordcloud = generate_wordcloud(neg_ngrams_dists[f'{options[ngram_type]}_gram'], colormap='autumn')
#             fig = render_wordcloud_figure(wordcloud)
#             st.pyplot(fig)
#         else:
#             chart = ngram_bar_chart(neg_ngrams_dists[f'{options[ngram_type]}_gram'], color='red')
#             st.altair_chart(chart, width='stretch')

@st.fragment
def render_ngram_section(title: str, data_key: str, options: dict, color: str, colormap: str, key_prefix: str):
    st.markdown(f"##### {title}")
    inner_cols = st.columns(4)
    
    with inner_cols[0]:
        ngram_type_key = st.selectbox(
            f'Select n-gram type for {title}', 
            options=list(options.keys()), 
            key=f'{key_prefix}_ngram_type', 
            label_visibility='collapsed'
        )
    
    with inner_cols[1]:
        toggle = st.toggle(
            'Chart / Cloud', 
            value=True, 
            key=f'{key_prefix}_ngram_toggle', 
            help=f'Toggle view for {title}.'
        )

    # Get data
    ngrams_dists = st.session_state[data_key]
    selected_gram = options[ngram_type_key] # e.g. '1', '2'
    data = ngrams_dists[f'{selected_gram}_gram']

    if toggle:
        # WordCloud
        wordcloud = generate_wordcloud(data, colormap=colormap)
        fig = render_wordcloud_figure(wordcloud)
        st.pyplot(fig)
    else:
        # Bar Chart
        chart = ngram_bar_chart(data, color=color)
        st.altair_chart(chart, width='stretch')


st.title('Content Analysis')

# --- CONTENT ANALYSIS PAGE ---
# CONTAINER FOR N-GRAM SECTIONS
with st.container():
    options = {'Unigram': '1', 'Bigram': '2', 'Trigram': '3'}
    col1, col2 = st.columns(2)
    
    with col1:
        render_ngram_section(
            title='Positive Reviews n-grams',
            data_key='positive_ngrams_dists',
            options=options,
            color='green',
            colormap='summer',
            key_prefix='pos'
        )
            
    with col2:
        render_ngram_section(
            title='Negative Reviews n-grams',
            data_key='negative_ngrams_dists',
            options=options,
            color='red',
            colormap='autumn',
            key_prefix='neg'
        )
# CONTAINER FOR DISTRIBUTION CHARTS
# with st.container():
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("##### Rating Distribution")
#         color_map = {'Positive': '#22c55e', 'Neutral': '#94a3b8', 'Negative': '#ef4444'}
#         chart = render_pie_chart(
#             st.session_state['df_filtered'],
#             column='sentiment_label',
#             colors=color_map
#             )
#         st.altair_chart(chart, width='stretch')
with st.container():
    st.subheader('Evidence Explorer')
    left_col, right_col = st.columns([1, 3], gap='large')
    with left_col:
        st.markdown("##### Search quotes")
        
        if 'query' not in st.session_state:
            st.session_state['query'] = ''
        query = st.text_input('Enter phrase to search',
                              placeholder='e.g., great product',
                              value=st.session_state['query']
                              )
        
        st.markdown('**Sort by:**')
        sort_by = st.radio('Sort by',
                           ['Latest', 'Highest Rating', 'Lowest Rating'],
                           index=0,
                           label_visibility='collapsed')
        
        st.markdown('**Filter by sentiment:**')
        sentiment_filter = st.multiselect('Filter by sentiment',
                                          options=['Positive', 'Neutral', 'Negative'],
                                          default=['Positive', 'Neutral', 'Negative'],
                                          label_visibility='collapsed')
        # Perform evidence search and store in session state
        st.session_state['evidence_df'] = evidence_search(
            st.session_state['df_filtered'],
            text=query,
            sort_by=sort_by,
            filter=sentiment_filter
        )
    with right_col:
        st.markdown('##### Search Results')
        st.dataframe(st.session_state['evidence_df'],
                     column_config={
                        'review_text': st.column_config.TextColumn(
                            'Review Text',
                            width='large',
                        ),
                        'rating': st.column_config.NumberColumn(
                            'Rating',
                            format='%d ⭐',
                        ),
                        'publish_time': st.column_config.DatetimeColumn(
                            'Published On',
                            format='YYYY-MM-DD',
                        ),
                        'sentiment_label': 'Sentiment'
                     },
                     hide_index=True)
        


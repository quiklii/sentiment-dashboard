# app/pages/content_analysis.py

import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from src.visualizations.wordcloud import generate_wordcloud, render_wordcloud_figure

from src.utils.logger import get_logger
logger = get_logger(__name__)

st.title('Content Analysis')

# --- CONTENT ANALYSIS PAGE ---
with st.container():
    options = {'Unigram': '1', 'Bigram': '2', 'Trigram': '3'}
    col1, col2 = st.columns(2)
    with col1:
        st.header('Positive Reviews n-grams')
        st.write('Choose the n-gram type')
        ngram_type = st.selectbox(
            'Select n-gram type for Positive Reviews', options=list(options.keys()), key='pos_ngram_type', width=120, label_visibility='collapsed')
        pos_ngrams_dists = st.session_state['positive_ngrams_dists']
        wordcloud = generate_wordcloud(pos_ngrams_dists[f'{options[ngram_type]}_gram'], colormap='summer')
        fig = render_wordcloud_figure(wordcloud)
        st.pyplot(fig)
    with col2:
        st.header('Negative Reviews n-grams')
        st.write('Choose the n-gram type')
        ngram_type = st.selectbox(
            'Select n-gram type for Negative Reviews', options=list(options.keys()), key='neg_ngram_type', width=120, label_visibility='collapsed')
        neg_ngrams_dists = st.session_state['negative_ngrams_dists']
        wordcloud = generate_wordcloud(neg_ngrams_dists[f'{options[ngram_type]}_gram'], colormap='autumn')
        fig = render_wordcloud_figure(wordcloud)
        st.pyplot(fig)
    






# src/visualizations/wordcloud.py

from wordcloud import WordCloud
import matplotlib.pyplot as plt

def prepare_ngram_wordcloud_dict(ngrams_dict: dict) -> dict:
    """Prepare a dictionary for word cloud generation from n-gram DataFrame."""
    
    freqs = {}
    
    for ngram, count in zip(ngrams_dict['ngram'], ngrams_dict['count']):
        if isinstance(ngram, tuple):
            label = ' '.join(ngram)
            label = label.replace(' ', '\u00A0')  # non-breaking space
        else:
            label = ngram
        
        freqs[label] = count
    return freqs

def generate_wordcloud(ngrams_dict: dict, colormap: str = 'viridis', width: int = 800, height: int = 400):
    """Generate a word cloud from frequency dictionary."""
    
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=None,
        colormap=colormap,
        max_words=50,
        mode='RGBA',
        random_state=7
    ).generate_from_frequencies(prepare_ngram_wordcloud_dict(ngrams_dict))
    return wordcloud

def render_wordcloud_figure(wordcloud, dpi=300):
    """Render a word cloud as a Matplotlib figure."""
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=dpi)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout(pad=0)
    return fig
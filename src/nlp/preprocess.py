# src/nlp/preprocess.py

from .load_spacy import load_spacy_model

def preprocess_text(text: str):
    """Preprocess the input text using SpaCy model."""
    nlp = load_spacy_model()
    doc = nlp(text)
    
    clean_tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return {'clean_tokens': clean_tokens} # return a dict with value as list of tokens

def extract_ngrams(tokens: tuple, n: int):
    """"Extract n-grams from a list(tuple) of tokens."""
    if len(tokens) < n:
        return []
    return [tokens[i:i+n] for i in range(len(tokens) - n + 1)] # - n + 1 for proper extraction of last n-gram     
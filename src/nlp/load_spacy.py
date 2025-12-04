# src/nlp/load_spacy.py

from functools import lru_cache
import spacy

from src.utils.logger import get_logger
logger = get_logger(__name__)

@lru_cache(maxsize=1)
def load_spacy_model():
    logger.info("Loading spaCy model: pl_core_news_md")
    try:
        nlp = spacy.load("pl_core_news_md")
        logger.info("spaCy model loaded successfully")
        return nlp
    except Exception as e:
        logger.error(f"Error loading spaCy model: {e}")
        raise e # may be unnecessary
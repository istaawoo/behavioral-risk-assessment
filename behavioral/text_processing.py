"""
Text processing: tokenization, keyword counting, sentiment, NER.
"""
import re
from typing import Dict, List
from utils import logger


def load_all_text_files(path: str) -> str:
    """
    Load all .txt files from a directory and concatenate them.
    
    Args:
        path: Directory path
    
    Returns:
        Concatenated text
    """
    from utils import load_text_files
    return load_text_files(path)


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words (lowercase, alphanumeric only).
    
    Args:
        text: Input text
    
    Returns:
        List of tokens
    """
    # Convert to lowercase and split on non-alphanumeric
    text_lower = text.lower()
    tokens = re.findall(r'\b[a-z0-9]+\b', text_lower)
    return tokens


def count_keywords(text: str, keywords: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Count occurrences of keywords in text.
    
    Args:
        text: Input text
        keywords: Dict mapping category -> list of keywords
    
    Returns:
        Dict mapping category -> count
    """
    text_lower = text.lower()
    counts = {}
    
    for category, word_list in keywords.items():
        count = 0
        for word in word_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word.lower()) + r'\b'
            matches = re.findall(pattern, text_lower)
            count += len(matches)
        counts[category] = count
    
    return counts


def compute_basic_stats(text: str) -> Dict:
    """
    Compute basic text statistics.
    
    Args:
        text: Input text
    
    Returns:
        Dict with word_count, sentence_count, avg_sentence_length
    """
    tokens = tokenize(text)
    word_count = len(tokens)
    
    # Improved sentence detection for transcripts
    # Split on punctuation OR newlines (common in transcripts)
    # Also consider common transcript markers like timestamps
    sentences = re.split(r'[.!?]+|\n{2,}', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    # If sentence count seems too low (transcripts without punctuation),
    # estimate based on word count (avg ~15-20 words per sentence)
    sentence_count = len(sentences)
    if word_count > 1000 and sentence_count < word_count / 100:
        # Likely a transcript with missing punctuation
        sentence_count = word_count // 18  # Estimate ~18 words per sentence
    
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    stats = {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_sentence_length, 2),
    }
    
    logger.info(f"Basic stats - Words: {word_count}, Sentences: {sentence_count}")
    return stats


def sentiment_score(text: str) -> float:
    """
    Compute sentiment score (0-1, where 0.5 is neutral).
    
    Tries to use TextBlob/VADER if available, falls back to lexicon-based approach.
    
    Args:
        text: Input text
    
    Returns:
        Sentiment score 0-1
    """
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        # TextBlob polarity is -1 to 1; normalize to 0-1
        polarity = blob.sentiment.polarity
        score = (polarity + 1) / 2
        logger.info(f"Sentiment (TextBlob): {score:.3f}")
        return score
    except ImportError:
        pass
    
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)
        compound = scores.get('compound', 0)
        # Compound is -1 to 1; normalize to 0-1
        score = (compound + 1) / 2
        logger.info(f"Sentiment (VADER): {score:.3f}")
        return score
    except ImportError:
        pass
    
    # Fallback: lexicon-based
    return _simple_sentiment(text)


def _simple_sentiment(text: str) -> float:
    """
    Simple lexicon-based sentiment (fallback).
    
    Args:
        text: Input text
    
    Returns:
        Sentiment score 0-1
    """
    positive_words = {
        "good", "great", "excellent", "amazing", "positive", "love", "happy",
        "better", "best", "fantastic", "wonderful", "awesome", "brilliant",
    }
    negative_words = {
        "bad", "poor", "terrible", "awful", "negative", "hate", "sad",
        "worse", "worst", "horrible", "disgusting", "disaster", "failure",
    }
    
    tokens = tokenize(text)
    token_set = set(tokens)
    
    positive_count = sum(1 for t in token_set if t in positive_words)
    negative_count = sum(1 for t in token_set if t in negative_words)
    
    total = positive_count + negative_count
    if total == 0:
        return 0.5  # Neutral
    
    score = positive_count / total
    logger.info(f"Sentiment (fallback lexicon): {score:.3f}")
    return score


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Simple NER: extract capitalized sequences (crude but no deps).
    
    Args:
        text: Input text
    
    Returns:
        Dict with 'entities' list
    """
    # Find sequences of capitalized words (crude NER)
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    entities = list(set(re.findall(pattern, text)))
    
    # Limit to top 20 most relevant
    entities = sorted(entities, key=len, reverse=True)[:20]
    
    logger.info(f"Extracted {len(entities)} named entities")
    return {"entities": entities}

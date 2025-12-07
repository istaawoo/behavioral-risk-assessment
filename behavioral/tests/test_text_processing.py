"""
Unit tests for text processing module.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from text_processing import (
    tokenize,
    count_keywords,
    compute_basic_stats,
    sentiment_score,
    extract_named_entities,
)


def test_tokenize():
    """Test tokenization."""
    text = "Hello, World! This is a test."
    tokens = tokenize(text)
    
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    assert "hello" in tokens
    assert "world" in tokens
    print("✓ test_tokenize passed")


def test_count_keywords():
    """Test keyword counting."""
    text = "Growth and expansion are key. We want rapid growth. Safety is important too."
    keywords = {
        "growth": ["growth", "expansion", "scale"],
        "safety": ["safety", "stable"],
    }
    
    counts = count_keywords(text, keywords)
    
    assert isinstance(counts, dict)
    assert counts["growth"] >= 2  # "growth" appears twice
    assert counts["safety"] >= 1  # "safety" appears once
    print("✓ test_count_keywords passed")


def test_compute_basic_stats():
    """Test basic statistics."""
    text = "This is a test. Another sentence here. And a third one!"
    stats = compute_basic_stats(text)
    
    assert "word_count" in stats
    assert "sentence_count" in stats
    assert "avg_sentence_length" in stats
    assert stats["word_count"] > 0
    assert stats["sentence_count"] >= 3
    print("✓ test_compute_basic_stats passed")


def test_sentiment_score():
    """Test sentiment analysis."""
    positive_text = "This is great and wonderful! I love it!"
    negative_text = "This is terrible and awful. I hate it."
    
    pos_score = sentiment_score(positive_text)
    neg_score = sentiment_score(negative_text)
    
    assert isinstance(pos_score, float)
    assert isinstance(neg_score, float)
    assert 0 <= pos_score <= 1
    assert 0 <= neg_score <= 1
    # Positive should score higher than negative
    assert pos_score > neg_score
    print("✓ test_sentiment_score passed")


def test_extract_named_entities():
    """Test named entity extraction."""
    text = "John Smith works at Apple Inc. Sarah Johnson joined Google last year."
    entities = extract_named_entities(text)
    
    assert "entities" in entities
    assert isinstance(entities["entities"], list)
    # Should extract some capitalized sequences
    assert len(entities["entities"]) > 0
    print("✓ test_extract_named_entities passed")


def run_all_tests():
    """Run all tests."""
    print("Running text_processing tests...\n")
    
    test_tokenize()
    test_count_keywords()
    test_compute_basic_stats()
    test_sentiment_score()
    test_extract_named_entities()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()

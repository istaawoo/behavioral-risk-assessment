"""
Unit tests for scoring module.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scoring import (
    normalize,
    compute_keyword_scores,
    compute_risk_tolerance_score,
    map_risk_label,
    compute_all_scores,
)


def test_normalize():
    """Test normalization function."""
    # Test basic normalization
    assert normalize(0, 0, 10) == 0.0
    assert normalize(10, 0, 10) == 1.0
    assert normalize(5, 0, 10) == 0.5
    
    # Test clamping
    assert normalize(15, 0, 10) == 1.0
    assert normalize(-5, 0, 10) == 0.0
    
    # Test inversion
    assert normalize(0, 0, 10, invert=True) == 1.0
    assert normalize(10, 0, 10, invert=True) == 0.0
    
    print("✓ test_normalize passed")


def test_compute_keyword_scores():
    """Test keyword score computation."""
    keyword_counts = {
        "growth": 10,
        "safety": 3,
        "momentum": 0,
        "volatility": 5,
        "emotional": 8,
    }
    word_count = 1000
    
    scores = compute_keyword_scores(keyword_counts, word_count)
    
    assert isinstance(scores, dict)
    assert all(0 <= v <= 1 for v in scores.values())
    assert "growth" in scores
    assert "safety" in scores
    # Growth mentions per 1000: 10, threshold 5 -> score 1.0
    assert scores["growth"] == 1.0
    
    print("✓ test_compute_keyword_scores passed")


def test_compute_risk_tolerance_score():
    """Test risk tolerance score."""
    quant_metrics = {
        "keyword_scores": {
            "growth": 0.8,
            "safety": 0.2,
            "momentum": 0.6,
            "volatility": 0.5,
            "emotional": 0.4,
        },
        "sentiment": 0.7,
    }
    
    score = compute_risk_tolerance_score(quant_metrics)
    
    assert isinstance(score, float)
    assert 0 <= score <= 1
    # High momentum, high sentiment -> higher risk score
    assert score > 0.5
    
    print("✓ test_compute_risk_tolerance_score passed")


def test_map_risk_label():
    """Test risk label mapping."""
    assert map_risk_label(0.1) == "Conservative"
    assert map_risk_label(0.3) == "Moderately Conservative"
    assert map_risk_label(0.5) == "Moderate"
    assert map_risk_label(0.7) == "Moderately Aggressive"
    assert map_risk_label(0.9) == "Aggressive"
    
    print("✓ test_map_risk_label passed")


def test_compute_all_scores():
    """Test comprehensive score computation."""
    keyword_counts = {
        "growth": 15,
        "safety": 5,
        "momentum": 2,
        "volatility": 8,
        "emotional": 10,
    }
    word_count = 2000
    sentiment = 0.6
    
    scores = compute_all_scores(keyword_counts, word_count, sentiment)
    
    assert isinstance(scores, dict)
    assert all(key in scores for key in [
        "growth_focus", "safety_focus", "momentum_bias",
        "volatility_tolerance", "emotional_intensity", "risk_tolerance"
    ])
    assert all(0 <= v <= 1 for v in scores.values())
    
    print("✓ test_compute_all_scores passed")


def run_all_tests():
    """Run all tests."""
    print("Running scoring tests...\n")
    
    test_normalize()
    test_compute_keyword_scores()
    test_compute_risk_tolerance_score()
    test_map_risk_label()
    test_compute_all_scores()
    
    print("\n✅ All scoring tests passed!")


if __name__ == "__main__":
    run_all_tests()

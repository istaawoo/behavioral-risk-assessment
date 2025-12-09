"""
Scoring: compute normalized quantitative scores (0-1 or 0-100).
"""
from typing import Dict
from utils import logger


def normalize(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
    """
    Normalize a value to 0-1 range.
    
    Args:
        value: Raw value to normalize
        min_val: Minimum expected value
        max_val: Maximum expected value
        invert: If True, invert score (1 - normalized_value)
    
    Returns:
        Normalized score 0-1, clamped
    """
    if max_val <= min_val:
        return 0.5
    
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0.0, min(1.0, normalized))  # Clamp to 0-1
    
    if invert:
        normalized = 1.0 - normalized
    
    return normalized


def compute_keyword_scores(keyword_counts: Dict[str, int], word_count: int) -> Dict[str, float]:
    """
    Compute normalized scores for keyword categories.
    
    Args:
        keyword_counts: Dict mapping category -> count
        word_count: Total word count (for normalization to per-1000)
    
    Returns:
        Dict mapping category -> score (0-1)
    """
    scores = {}
    
    if word_count == 0:
        for category in keyword_counts:
            scores[category] = 0.0
        return scores
    
    # Normalize to mentions per 1000 words
    rate_per_1000 = {
        cat: (count / word_count * 1000) if word_count > 0 else 0
        for cat, count in keyword_counts.items()
    }
    
    # Define thresholds for each category (these are editable weights)
    # Lower thresholds = higher scores for the same mention counts
    thresholds = {
        "growth": 0.3,      # up to 0.3 mentions per 1000 words = score 1.0 (extremely sensitive)
        "safety": 3.0,      # up to 3 mentions per 1000 words = score 1.0
        "momentum": 0.10,   # up to 0.10 mentions per 1000 words = score 1.0 (very sensitive)
        "volatility": 0.2,  # up to 0.2 mentions per 1000 words = score 1.0 (extremely sensitive)
        "emotional": 3.0,   # up to 3 mentions per 1000 words = score 1.0 (more sensitive)
    }
    
    for category, rate in rate_per_1000.items():
        threshold = thresholds.get(category, 5.0)
        score = normalize(rate, 0, threshold)
        scores[category] = score
    
    logger.info(f"Keyword rates per 1000: {rate_per_1000}")
    logger.info(f"Keyword scores: {scores}")
    return scores


def compute_risk_tolerance_score(
    quant_metrics: Dict,
    weights: Dict[str, float] = None,
) -> float:
    """
    Compute overall risk tolerance score (0-1).
    
    Formula (calibrated for moderately aggressive to aggressive outcomes):
        risk_score = 0.40*growth_focus + 0.35*momentum_bias + 0.25*sentiment - 0.15*safety_focus + 0.20
    
    The +0.20 baseline boost ensures profiles trend toward moderate-aggressive to aggressive range.
    
    These weights are editable; adjust as needed per behavioral analysis.
    
    Args:
        quant_metrics: Dict with keyword_scores, sentiment, etc.
        weights: Optional custom weights dict
    
    Returns:
        Risk tolerance score 0-1
    """
    if weights is None:
        # Boosted weights: favor growth/momentum/sentiment more heavily
        weights = {
            "growth": 0.45,     # Growth focus is a primary indicator
            "momentum": 0.40,   # Momentum signals strong confidence
            "sentiment": 0.30,  # Optimism strongly correlates with risk-taking
            "safety": -0.18,    # Safety focus reduces risk appetite
            "baseline": 0.30,   # Higher baseline boost to reach moderately aggressive range
        }
    
    keyword_scores = quant_metrics.get("keyword_scores", {})
    sentiment = quant_metrics.get("sentiment", 0.5)
    
    growth_focus = keyword_scores.get("growth", 0.0)
    momentum_bias = keyword_scores.get("momentum", 0.0)
    safety_focus = keyword_scores.get("safety", 0.0)
    volatility_tolerance = keyword_scores.get("volatility", 0.0)
    
    # Compute weighted sum with baseline boost
    score = (
        weights.get("growth", 0.4) * growth_focus
        + weights.get("momentum", 0.35) * momentum_bias
        + weights.get("sentiment", 0.25) * sentiment
        + weights.get("safety", -0.15) * safety_focus
        + weights.get("baseline", 0.15)  # Baseline shift toward aggressive
    )
    
    # Clamp to 0-1
    score = max(0.0, min(1.0, score))
    
    logger.info(f"Risk tolerance score: {score:.3f}")
    return score


def map_risk_label(score: float) -> str:
    """
    Map risk score (0-1) to categorical label.
    
    Args:
        score: Risk tolerance score 0-1
    
    Returns:
        Risk tolerance label
    """
    if score < 0.2:
        return "Conservative"
    elif score < 0.4:
        return "Moderately Conservative"
    elif score < 0.6:
        return "Moderate"
    elif score < 0.8:
        return "Moderately Aggressive"
    else:
        return "Aggressive"


def compute_all_scores(
    keyword_counts: Dict[str, int],
    word_count: int,
    sentiment: float,
) -> Dict:
    """
    Compute all quantitative scores.
    
    Args:
        keyword_counts: Dict of keyword category counts
        word_count: Total word count
        sentiment: Sentiment score 0-1
    
    Returns:
        Dict with all scores
    """
    keyword_scores = compute_keyword_scores(keyword_counts, word_count)
    
    quant_metrics = {
        "keyword_scores": keyword_scores,
        "sentiment": sentiment,
    }
    
    risk_score = compute_risk_tolerance_score(quant_metrics)
    
    return {
        "growth_focus": keyword_scores.get("growth", 0.0),
        "safety_focus": keyword_scores.get("safety", 0.0),
        "momentum_bias": keyword_scores.get("momentum", 0.0),
        "volatility_tolerance": keyword_scores.get("volatility", 0.0),
        "emotional_intensity": keyword_scores.get("emotional", 0.0),
        "risk_tolerance": risk_score,
    }

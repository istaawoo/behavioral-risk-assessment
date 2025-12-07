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
    thresholds = {
        "growth": 5.0,      # up to 5 mentions per 1000 words = score 1.0
        "safety": 3.0,      # up to 3 mentions per 1000 words = score 1.0
        "momentum": 0.2,    # up to 0.2 mentions per 1000 words = score 1.0
        "volatility": 3.0,  # up to 3 mentions per 1000 words = score 1.0
        "emotional": 5.0,   # up to 5 mentions per 1000 words = score 1.0
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
    
    Formula:
        risk_score = 0.5*momentum_bias + 0.3*sentiment + 0.2*volatility_tolerance - 0.1*safety_focus
    
    These weights are editable; adjust as needed per behavioral analysis.
    
    Args:
        quant_metrics: Dict with keyword_scores, sentiment, etc.
        weights: Optional custom weights dict
    
    Returns:
        Risk tolerance score 0-1
    """
    if weights is None:
        # Default weights: tune these to emphasize different factors
        weights = {
            "momentum": 0.5,
            "sentiment": 0.3,
            "volatility": 0.2,
            "safety": -0.1,  # Negative weight: high safety focus lowers risk score
        }
    
    keyword_scores = quant_metrics.get("keyword_scores", {})
    sentiment = quant_metrics.get("sentiment", 0.5)
    
    momentum_bias = keyword_scores.get("momentum", 0.0)
    safety_focus = keyword_scores.get("safety", 0.0)
    volatility_tolerance = keyword_scores.get("volatility", 0.0)
    
    # Compute weighted sum
    score = (
        weights.get("momentum", 0.5) * momentum_bias
        + weights.get("sentiment", 0.3) * sentiment
        + weights.get("volatility", 0.2) * volatility_tolerance
        + weights.get("safety", -0.1) * safety_focus
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

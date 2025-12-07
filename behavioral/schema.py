"""
JSON schema and dataclass definitions for behavioral profiles.
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Metadata:
    """Metadata for the behavioral profile."""
    created_at: str
    source_files: List[str]
    llm_used: bool


@dataclass
class QuantitativeMetrics:
    """Quantitative metrics from text analysis."""
    word_count: int
    sentence_count: int
    mentions: Dict[str, int]
    sentiment: float
    keyword_rates_per_1000: Dict[str, float]
    scores: Dict[str, float]


@dataclass
class QualitativeProfile:
    """Qualitative profile from LLM analysis."""
    risk_tolerance_label: str
    traits: List[str]
    biases: List[str]
    narrative: str


@dataclass
class Recommendations:
    """Recommendations based on analysis."""
    portfolio_modifier: str
    sector_pref: List[str]
    notes: str


@dataclass
class BehavioralProfile:
    """Complete behavioral profile."""
    metadata: Metadata
    quantitative: QuantitativeMetrics
    qualitative: QualitativeProfile
    recommendations: Recommendations
    
    def to_dict(self) -> Dict:
        """Convert to dictionary (for JSON serialization)."""
        return {
            "metadata": asdict(self.metadata),
            "quantitative": asdict(self.quantitative),
            "qualitative": asdict(self.qualitative),
            "recommendations": asdict(self.recommendations),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "BehavioralProfile":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            metadata=Metadata(**data["metadata"]),
            quantitative=QuantitativeMetrics(**data["quantitative"]),
            qualitative=QualitativeProfile(**data["qualitative"]),
            recommendations=Recommendations(**data["recommendations"]),
        )


def create_stub_profile(
    source_files: List[str],
    word_count: int,
    sentence_count: int,
    keyword_counts: Dict[str, int],
    sentiment: float,
    scores: Dict[str, float],
) -> BehavioralProfile:
    """
    Create a minimal behavioral profile (stub, no LLM).
    
    Args:
        source_files: List of source file names
        word_count: Total words
        sentence_count: Total sentences
        keyword_counts: Dict of keyword category counts
        sentiment: Sentiment score 0-1
        scores: Dict of computed scores
    
    Returns:
        BehavioralProfile instance
    """
    keyword_rates = {
        cat: (count / word_count * 1000) if word_count > 0 else 0
        for cat, count in keyword_counts.items()
    }
    
    profile = BehavioralProfile(
        metadata=Metadata(
            created_at=datetime.utcnow().isoformat() + "Z",
            source_files=source_files,
            llm_used=False,
        ),
        quantitative=QuantitativeMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            mentions=keyword_counts,
            sentiment=round(sentiment, 3),
            keyword_rates_per_1000={k: round(v, 2) for k, v in keyword_rates.items()},
            scores={k: round(v, 3) for k, v in scores.items()},
        ),
        qualitative=QualitativeProfile(
            risk_tolerance_label="Pending LLM Analysis",
            traits=[],
            biases=[],
            narrative="Run with --llm-on True to generate qualitative analysis.",
        ),
        recommendations=Recommendations(
            portfolio_modifier="No recommendations without qualitative analysis",
            sector_pref=[],
            notes="Quantitative metrics suggest analyzing further with LLM.",
        ),
    )
    
    return profile

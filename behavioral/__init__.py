"""
Behavioral Risk Assessment Module

Analyzes investment psychology and behavioral patterns from text.
"""

__version__ = "1.0.0"

from .behavioral_runner import run_analysis
from .schema import BehavioralProfile
from .utils import KEYWORD_CATEGORIES

__all__ = [
    "run_analysis",
    "BehavioralProfile",
    "KEYWORD_CATEGORIES",
]

"""
Utility functions: file loading, logging, keyword definitions.
"""
import logging
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Default keyword categories for behavioral analysis
KEYWORD_CATEGORIES = {
    "growth": [
        "growth",
        "scale",
        "expand",
        "disrupt",
        "hypergrowth",
        "cagr",
        "scaleup",
        "explosive",
        "multiplier",
        "unicorn",
    ],
    "safety": [
        "dividend",
        "yield",
        "income",
        "stable",
        "defensive",
        "moat",
        "resilient",
        "steady",
        "conservative",
        "capital preservation",
    ],
    "momentum": [
        "buy",
        "hold",
        "momentum",
        "swing",
        "bet",
        "conviction",
        "all-in",
        "bullish",
        "surge",
        "rally",
    ],
    "volatility": [
        "swing",
        "volatile",
        "volatility",
        "ride out",
        "long-term",
        "short-term",
        "fluctuation",
        "downside",
        "drawdown",
        "crash",
    ],
    "emotional": [
        "excited",
        "fear",
        "worried",
        "confident",
        "pride",
        "uncertain",
        "anxious",
        "optimistic",
        "pessimistic",
        "bullish",
    ],
}


def load_text_files(directory: str) -> str:
    """
    Load all .txt files from a directory and concatenate them.
    
    Args:
        directory: Path to directory containing .txt files
    
    Returns:
        Concatenated string of all text file contents
    """
    path = Path(directory)
    if not path.exists():
        logger.warning(f"Directory {directory} does not exist. Returning empty string.")
        return ""
    
    all_text = []
    txt_files = list(path.glob("*.txt"))
    
    if not txt_files:
        logger.warning(f"No .txt files found in {directory}")
        return ""
    
    for txt_file in sorted(txt_files):
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()
                all_text.append(content)
                logger.info(f"Loaded {txt_file.name} ({len(content)} chars)")
        except Exception as e:
            logger.error(f"Failed to load {txt_file.name}: {e}")
    
    result = "\n".join(all_text)
    logger.info(f"Total text loaded: {len(result)} characters from {len(txt_files)} files")
    return result


def save_json(data: dict, filepath: str) -> None:
    """
    Save a dictionary as JSON with pretty formatting.
    
    Args:
        data: Dictionary to save
        filepath: Path to output JSON file
    """
    import json
    
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved JSON to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save JSON to {filepath}: {e}")
        raise


def load_json(filepath: str) -> dict:
    """
    Load JSON from file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Loaded dictionary
    """
    import json
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {filepath}: {e}")
        raise


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger."""
    return logging.getLogger(name)

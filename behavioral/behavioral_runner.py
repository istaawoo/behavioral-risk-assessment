"""
Main behavioral risk analysis runner.

Orchestrates text loading, processing, scoring, and optional LLM analysis.
Outputs JSON profile conforming to schema.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from utils import load_text_files, save_json, get_logger, KEYWORD_CATEGORIES
from text_processing import (
    load_all_text_files,
    tokenize,
    count_keywords,
    compute_basic_stats,
    sentiment_score,
    extract_named_entities,
)
from scoring import compute_all_scores, map_risk_label
from schema import BehavioralProfile, Metadata, QuantitativeMetrics, QualitativeProfile, Recommendations
from llm_client import call_llm, prepare_llm_prompt, LLM_ENABLED

logger = get_logger(__name__)


def run_analysis(
    input_dir: str = "behavioral_data",
    output_file: str = "output/behavioral_profile.json",
    llm_enabled: bool = False,
) -> BehavioralProfile:
    """
    Main analysis pipeline.
    
    Steps:
    1. Load all text files from input_dir
    2. Compute quantitative metrics
    3. Compute scores
    4. Optionally call LLM for qualitative analysis
    5. Merge and save to output_file
    
    Args:
        input_dir: Directory with text files
        output_file: Path to output JSON
        llm_enabled: Whether to enable LLM analysis
    
    Returns:
        BehavioralProfile instance
    """
    logger.info(f"Starting behavioral analysis on {input_dir}")
    
    # Step 1: Load text
    logger.info("Step 1: Loading text files...")
    text = load_all_text_files(input_dir)
    
    if not text.strip():
        logger.error(f"No text data found in {input_dir}")
        raise ValueError(f"No text data in {input_dir}")
    
    # Get source file names
    input_path = Path(input_dir)
    source_files = [f.name for f in sorted(input_path.glob("*.txt"))]
    logger.info(f"Loaded {len(source_files)} files: {source_files}")
    
    # Step 2: Compute quantitative metrics
    logger.info("Step 2: Computing quantitative metrics...")
    tokens = tokenize(text)
    word_count = len(tokens)
    
    basic_stats = compute_basic_stats(text)
    sentence_count = basic_stats["sentence_count"]
    
    keyword_counts = count_keywords(text, KEYWORD_CATEGORIES)
    sentiment = sentiment_score(text)
    
    logger.info(f"Text stats - Words: {word_count}, Sentences: {sentence_count}")
    logger.info(f"Keyword counts: {keyword_counts}")
    logger.info(f"Sentiment: {sentiment:.3f}")
    
    # Step 3: Compute scores
    logger.info("Step 3: Computing scores...")
    scores = compute_all_scores(keyword_counts, word_count, sentiment)
    risk_score = scores.get("risk_tolerance", 0.5)
    risk_label = map_risk_label(risk_score)
    
    logger.info(f"Scores computed: {scores}")
    logger.info(f"Risk tolerance: {risk_label} ({risk_score:.3f})")
    
    # Step 4: Optional LLM analysis
    logger.info("Step 4: Qualitative analysis (LLM)...")
    llm_used = False
    qualitative_data = {
        "risk_tolerance_label": risk_label,
        "traits": [],
        "biases": [],
        "narrative": "",
    }
    recommendations_data = {
        "portfolio_modifier": "",
        "sector_pref": [],
        "notes": "",
    }
    
    # First, check for manual LLM file (user-provided via ChatGPT/Gemini)
    manual_llm_path = Path("output/llm_qualitative.json")
    if manual_llm_path.exists():
        try:
            logger.info("Found manual LLM file at output/llm_qualitative.json")
            import json
            with open(manual_llm_path, 'r') as f:
                llm_response = json.load(f)
            
            qualitative_data.update({
                "risk_tolerance_label": llm_response.get("risk_tolerance_label", risk_label),
                "traits": llm_response.get("traits", []),
                "biases": llm_response.get("biases", []),
                "narrative": llm_response.get("narrative", ""),
            })
            
            rec_data = llm_response.get("recommendations", {})
            recommendations_data.update({
                "portfolio_modifier": rec_data.get("portfolio_modifier", ""),
                "sector_pref": rec_data.get("sector_pref", []),
                "notes": rec_data.get("notes", ""),
            })
            
            llm_used = True
            logger.info("Manual LLM analysis loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load manual LLM file: {e}")
    
    # If no manual file and LLM enabled, try API call
    elif llm_enabled:
        try:
            logger.info("Attempting LLM analysis...")
            prompt = prepare_llm_prompt(text, max_tokens=5000)
            llm_response = call_llm(prompt)
            
            if llm_response:
                qualitative_data.update({
                    "risk_tolerance_label": llm_response.get("risk_tolerance_label", risk_label),
                    "traits": llm_response.get("traits", []),
                    "biases": llm_response.get("biases", []),
                    "narrative": llm_response.get("narrative", ""),
                })
                
                rec_data = llm_response.get("recommendations", {})
                recommendations_data.update({
                    "portfolio_modifier": rec_data.get("portfolio_modifier", ""),
                    "sector_pref": rec_data.get("sector_pref", []),
                    "notes": rec_data.get("notes", ""),
                })
                
                llm_used = True
                logger.info("LLM analysis successful")
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}. Continuing with quantitative-only profile.")
    
    # If no LLM data at all, provide default message
    if not llm_used and not qualitative_data["narrative"]:
        qualitative_data["narrative"] = (
            "Qualitative analysis not available. "
            "Use the Streamlit UI to download text corpus and analyze with ChatGPT/Gemini, "
            "then save response as output/llm_qualitative.json and re-run."
        )
    
    # Step 5: Assemble profile
    logger.info("Step 5: Assembling final profile...")
    
    keyword_rates = {
        cat: round((count / word_count * 1000) if word_count > 0 else 0, 2)
        for cat, count in keyword_counts.items()
    }
    
    profile = BehavioralProfile(
        metadata=Metadata(
            created_at=datetime.utcnow().isoformat() + "Z",
            source_files=source_files,
            llm_used=llm_used,
        ),
        quantitative=QuantitativeMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            mentions=keyword_counts,
            sentiment=round(sentiment, 3),
            keyword_rates_per_1000=keyword_rates,
            scores={k: round(v, 3) for k, v in scores.items()},
        ),
        qualitative=QualitativeProfile(
            risk_tolerance_label=qualitative_data["risk_tolerance_label"],
            traits=qualitative_data["traits"],
            biases=qualitative_data["biases"],
            narrative=qualitative_data["narrative"],
        ),
        recommendations=Recommendations(
            portfolio_modifier=recommendations_data["portfolio_modifier"],
            sector_pref=recommendations_data["sector_pref"],
            notes=recommendations_data["notes"],
        ),
    )
    
    # Save JSON
    logger.info(f"Step 6: Saving to {output_file}...")
    save_json(profile.to_dict(), output_file)
    logger.info(f"Analysis complete. Output saved to {output_file}")
    
    return profile


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Behavioral Risk Analysis - analyze text for investment psychology."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="behavioral_data",
        help="Input directory with .txt files (default: behavioral_data)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/behavioral_profile.json",
        help="Output JSON file path (default: output/behavioral_profile.json)",
    )
    parser.add_argument(
        "--llm-on",
        type=str,
        default="False",
        help="Enable LLM analysis (True/False, default: False)",
    )
    
    args = parser.parse_args()
    llm_enabled = args.llm_on.lower() in ("true", "1", "yes")
    
    try:
        profile = run_analysis(
            input_dir=args.input,
            output_file=args.output,
            llm_enabled=llm_enabled,
        )
        print(f"\n✅ Analysis complete. Profile saved to {args.output}")
        print(f"   Risk Tolerance: {profile.qualitative.risk_tolerance_label}")
        print(f"   LLM Used: {profile.metadata.llm_used}")
        print(f"   Word Count: {profile.quantitative.word_count}")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

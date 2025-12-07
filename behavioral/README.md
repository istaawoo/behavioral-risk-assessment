# Behavioral Risk Assessment Module

Analyze investment psychology and behavioral biases from local text data. This module processes text transcripts (LinkedIn posts, podcast interviews, social media, etc.) to generate a quantitative + qualitative profile of investment behavior and risk tolerance.

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r ../requirements.txt
```

### Running Locally

#### Option 1: Command Line (Quantitative Only, Fast)

```bash
python behavioral_runner.py --input behavioral_data --output output/behavioral_profile.json --llm-on False
```

#### Option 2: With LLM Analysis (Qualitative + Quantitative)

```bash
# Set API key first
export LLM_API_KEY="your-openai-api-key"  # or set in environment

python behavioral_runner.py --input behavioral_data --output output/behavioral_profile.json --llm-on True
```

#### Option 3: Streamlit UI (Interactive)

```bash
streamlit run streaming_ui.py
```

This opens a web interface where you can:
- Select input directory
- Toggle LLM analysis
- View results with pretty visualizations
- Download JSON profile

## Input Format

Place text files (`.txt`) in the `behavioral_data/` directory. The module reads all `.txt` files and analyzes them together.

Example files:
- `linkedin.txt` – LinkedIn posts or articles
- `podcast_transcript.txt` – Interview or podcast transcript
- `social_posts.txt` – Twitter, Instagram, or social media captions

No special formatting required; plain text is processed as-is.

## Output: JSON Schema

The analysis generates a JSON profile in `output/behavioral_profile.json`:

```json
{
  "metadata": {
    "created_at": "2025-12-06T12:34:56.789Z",
    "source_files": ["linkedin.txt", "podcast_transcript.txt"],
    "llm_used": true
  },
  "quantitative": {
    "word_count": 2850,
    "sentence_count": 58,
    "mentions": {
      "growth": 12,
      "safety": 4,
      "momentum": 3,
      "volatility": 5,
      "emotional": 8
    },
    "sentiment": 0.62,
    "keyword_rates_per_1000": {
      "growth": 4.21,
      "safety": 1.40,
      "momentum": 1.05,
      "volatility": 1.75,
      "emotional": 2.81
    },
    "scores": {
      "growth_focus": 0.842,
      "safety_focus": 0.467,
      "momentum_bias": 0.525,
      "volatility_tolerance": 0.583,
      "emotional_intensity": 0.562,
      "risk_tolerance": 0.68
    }
  },
  "qualitative": {
    "risk_tolerance_label": "Moderately Aggressive",
    "traits": ["growth-oriented", "confident", "momentum-driven"],
    "biases": ["overconfidence_bias", "momentum_bias"],
    "narrative": "Subject exhibits strong preference for growth and scaling opportunities..."
  },
  "recommendations": {
    "portfolio_modifier": "increase_equities_by_5pct_if_currently_underweight",
    "sector_pref": ["Technology", "Semiconductors", "Cloud Computing"],
    "notes": "Subject shows high conviction in tech disruption. Monitor for overconcentration risk."
  }
}
```

## JSON Schema Fields

### Metadata
- `created_at` – ISO timestamp of analysis
- `source_files` – List of input file names
- `llm_used` – Whether LLM was called

### Quantitative Metrics
- `word_count` – Total words analyzed
- `sentence_count` – Total sentences
- `mentions` – Raw keyword counts by category
- `sentiment` – Overall sentiment (0–1, where 0.5 = neutral)
- `keyword_rates_per_1000` – Keyword mentions normalized per 1000 words
- `scores` – Normalized behavioral scores (0–1):
  - `growth_focus` – Emphasis on expansion and hypergrowth
  - `safety_focus` – Emphasis on stability and defensive positioning
  - `momentum_bias` – Tendency to follow momentum plays
  - `volatility_tolerance` – Comfort with market swings
  - `emotional_intensity` – Emotional language intensity
  - `risk_tolerance` – Combined risk score (0–1)

### Qualitative Profile (LLM-Generated)
- `risk_tolerance_label` – Categorical: Conservative, Moderately Conservative, Moderate, Moderately Aggressive, Aggressive
- `traits` – Identified personality traits (e.g., "growth-oriented", "data-driven")
- `biases` – Behavioral biases (e.g., "overconfidence_bias", "recency_bias")
- `narrative` – Detailed text summary of investment psychology

### Recommendations
- `portfolio_modifier` – Suggested portfolio adjustment
- `sector_pref` – Preferred sectors based on behavior
- `notes` – Risk warnings or considerations

## How Stock Analyzer Consumes This

The `behavioral_profile.json` provides two key inputs for portfolio construction:

1. **Quantitative Scores** – Direct use in portfolio weighting:
   - `risk_tolerance` → Portfolio stock/bond allocation
   - `growth_focus` → Overweight growth equities
   - `volatility_tolerance` → Position sizing and leverage decisions

2. **Qualitative Profile** – Constraint and preference input:
   - `sector_pref` → Sector allocation limits
   - `traits` → Heuristics for style selection
   - `narrative` → Context for portfolio reviewer

Example: High `growth_focus` (0.84) + high `risk_tolerance` (0.68) → 75% equities, heavy tech weighting.

## Scoring Formulas (Editable Weights)

All scoring is deterministic and documented:

```python
# Keyword scores: normalized by thresholds
growth_score = normalize(mentions_per_1000, 0, 5)  # 5 = max threshold

# Risk tolerance (weighted combination):
risk_score = (
    0.5 * momentum_bias
    + 0.3 * sentiment
    + 0.2 * volatility_tolerance
    - 0.1 * safety_focus
)

# Normalize to 0-1, then map to label
label = map_to_label(risk_score)
```

**To adjust weights**, edit `behavioral/scoring.py`:

```python
def compute_risk_tolerance_score(quant_metrics, weights=None):
    if weights is None:
        weights = {
            "momentum": 0.5,    # <-- Change these
            "sentiment": 0.3,
            "volatility": 0.2,
            "safety": -0.1,
        }
```

## Keyword Categories (Customizable)

Edit `behavioral/utils.py` to modify keyword lists:

```python
KEYWORD_CATEGORIES = {
    "growth": ["growth", "scale", "expand", "disrupt", "hypergrowth", ...],
    "safety": ["dividend", "yield", "stable", "defensive", ...],
    "momentum": ["buy", "momentum", "swing", "conviction", ...],
    "volatility": ["volatile", "drawdown", "ride out", ...],
    "emotional": ["excited", "confident", "worried", ...],
}
```

Add new categories or modify existing ones as needed.

## LLM Integration & Cost

### Enabled / Disabled

The module respects the `--llm-on` flag:
- `--llm-on False` (default) – Runs quantitative-only analysis. ~0 cost.
- `--llm-on True` – Calls LLM for qualitative insights. Cost applies.

### API Setup

To use LLM:

1. Set environment variable:
   ```bash
   export LLM_API_KEY="sk-..."  # OpenAI key
   ```

2. Or hardcode in code (not recommended):
   ```python
   os.environ["LLM_API_KEY"] = "sk-..."
   ```

3. LLM prompt is automatically trimmed to ~5000 tokens (~20k characters).

### Cost Estimate

- **Model**: gpt-3.5-turbo or gpt-4o (configurable)
- **Typical cost per call**: $0.01 – $0.30
- **Optimization**: Run quantitative analysis first, then run LLM once and cache the JSON

**Recommendation**: Run without LLM (`--llm-on False`) initially. If insights are needed, run once with LLM enabled and reuse the JSON.

## Testing

```bash
# Run all tests
cd behavioral/tests
python test_text_processing.py
python test_scoring.py

# Or use pytest
pip install pytest
pytest behavioral/tests/
```

Tests validate:
- Tokenization and keyword counting
- Sentiment scoring (fallback lexicon)
- Score normalization and clamping
- JSON schema compliance

## Troubleshooting

### No input files found
- Ensure `.txt` files are in the `behavioral_data/` directory
- Check file encoding (must be UTF-8)

### Sentiment score always 0.5
- TextBlob/VADER not installed. Install with: `pip install textblob nltk`
- If unavailable, module falls back to simple lexicon (less accurate)

### LLM call fails
- Check `LLM_API_KEY` is set and valid
- Check API rate limits
- Review error logs for details
- Run without LLM (`--llm-on False`) as fallback

### JSON parsing error on LLM response
- LLM output parsing is robust (handles markdown, code blocks, etc.)
- If still failing, check logs for raw response
- Consider shorter input text (token limits)

## File Structure

```
behavioral/
├── __init__.py                 # Package init
├── behavioral_runner.py        # Main analysis pipeline
├── streaming_ui.py             # Streamlit UI wrapper
├── text_processing.py          # Text tokenization, keywords, sentiment
├── scoring.py                  # Score computation & formulas
├── llm_client.py               # LLM call interface (safe, isolated)
├── schema.py                   # JSON dataclass definitions
├── utils.py                    # Utilities, keywords, logging
├── tests/
│   ├── __init__.py
│   ├── test_text_processing.py
│   └── test_scoring.py
└── README.md                   # This file

behavioral_data/               # Input text files (create and populate)
├── linkedin.txt
├── podcast_transcript.txt
└── social_posts.txt

output/                        # Output directory (auto-created)
└── behavioral_profile.json    # Generated profile
```

## Architecture Notes

### Design Principles

1. **No Live APIs** – All input is local files. No social media scraping or external APIs except optional LLM.

2. **Deterministic** – Same input always produces same quantitative scores.

3. **LLM is Optional** – Module works fully offline. LLM adds qualitative depth only.

4. **Testable** – Each component has unit tests. Scoring formulas are explicit and tunable.

5. **Readable Logs** – All major steps are logged for debugging and transparency.

### Module Responsibilities

- **text_processing.py** – Converts raw text to metrics (counts, sentiment, entities)
- **scoring.py** – Normalizes metrics into 0–1 scores with editable weights
- **llm_client.py** – Encapsulates LLM calls with fallback stubs
- **schema.py** – JSON structure definitions (dataclasses)
- **behavioral_runner.py** – Orchestrates pipeline; handles I/O
- **streaming_ui.py** – Streamlit interface for interactive use
- **utils.py** – Keywords, logging, file I/O helpers

## License

See LICENSE in repository root.

## Contributing

To modify behavior:

1. **Change keyword thresholds** → Edit `behavioral/scoring.py`
2. **Add new keyword categories** → Edit `behavioral/utils.py`
3. **Adjust risk formula weights** → Edit `compute_risk_tolerance_score()` in `behavioral/scoring.py`
4. **Improve LLM prompt** → Edit `LLM_USER_PROMPT_TEMPLATE` in `behavioral/llm_client.py`
5. **Add sentiment sources** – Extend `sentiment_score()` in `behavioral/text_processing.py`

All changes are immediately reflected on next run (no recompilation needed).

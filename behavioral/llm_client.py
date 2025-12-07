"""
LLM client: encapsulate LLM calls with safe, isolated interface.
"""
import os
import json
from typing import Dict, Optional
from utils import logger


# Global flag to enable/disable LLM calls
LLM_ENABLED = os.environ.get("LLM_ENABLED", "False").lower() in ("true", "1", "yes")


def call_llm(
    prompt: str,
    api_key_env: str = "LLM_API_KEY",
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 1500,
) -> Dict:
    """
    Call an LLM (OpenAI or fallback stub).
    
    Args:
        prompt: User prompt (pre-trimmed to ~5k tokens)
        api_key_env: Environment variable name for API key
        model: Model name (e.g., "gpt-3.5-turbo", "gpt-4")
        max_tokens: Max tokens in response
    
    Returns:
        Parsed JSON response as dict
    """
    api_key = os.environ.get(api_key_env)
    
    if not LLM_ENABLED or not api_key:
        logger.warning(
            f"LLM disabled or no API key found. Returning deterministic stub."
        )
        return _get_stub_response()
    
    try:
        import requests
    except ImportError:
        logger.error("requests library not found. Install with: pip install requests")
        return _get_stub_response()
    
    # Call OpenAI API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        
        data = response.json()
        message_content = data["choices"][0]["message"]["content"]
        
        # Parse JSON response
        parsed = _parse_json_response(message_content)
        logger.info("LLM response successfully parsed")
        return parsed
    
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM API call failed: {e}")
        return _get_stub_response()
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return _get_stub_response()


def _parse_json_response(content: str) -> Dict:
    """
    Robustly parse JSON from LLM response.
    
    Handles cases where LLM returns markdown code blocks or extraneous text.
    
    Args:
        content: Raw LLM response
    
    Returns:
        Parsed JSON as dict
    """
    # Try direct JSON parse first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code block
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end > start:
            try:
                return json.loads(content[start:end].strip())
            except json.JSONDecodeError:
                pass
    
    # Try to extract JSON from generic code block
    if "```" in content:
        start = content.find("```") + 3
        end = content.find("```", start)
        if end > start:
            try:
                return json.loads(content[start:end].strip())
            except json.JSONDecodeError:
                pass
    
    # Last resort: look for JSON object pattern
    import re
    match = re.search(r'\{[\s\S]*\}', content)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    logger.warning("Could not parse JSON from LLM response. Returning stub.")
    return _get_stub_response()


def _get_stub_response() -> Dict:
    """
    Return deterministic stub response for offline/fallback use.
    
    Returns:
        Stub qualitative profile dict
    """
    return {
        "risk_tolerance_label": "Moderate",
        "traits": ["data-driven", "cautious"],
        "biases": ["anchoring_bias"],
        "narrative": "This is a stub response generated because LLM is disabled or unavailable. "
                     "Run with LLM_ENABLED=True and a valid API key to get personalized analysis.",
        "recommendations": {
            "portfolio_modifier": "maintain_current_allocation",
            "sector_pref": ["Technology", "Healthcare"],
            "notes": "Stub response. See narrative for details.",
        },
    }


# LLM Prompt Template
SYSTEM_PROMPT = (
    "You are an objective financial behavioral analyst. "
    "Return ONLY valid JSON, with no markdown or additional text. "
    "Do not include code blocks or formatting."
)

LLM_USER_PROMPT_TEMPLATE = (
    "Below is a corpus of text data from a person's public statements, social posts, and interviews. "
    "Analyze their investment psychology, risk temperament, common behavioral biases, "
    "and provide practical portfolio recommendations.\n\n"
    "Use explicit, evidence-backed statements: for each claim, provide 1-2 supporting quotes or keyword counts.\n\n"
    "CORPUS:\n{corpus}\n\n"
    "Return ONLY a JSON object with these keys:\n"
    "- risk_tolerance_label: One of [Conservative, Moderately Conservative, Moderate, Moderately Aggressive, Aggressive]\n"
    "- traits: List of personality traits (max 5)\n"
    "- biases: List of identified cognitive biases (max 5)\n"
    "- narrative: Concise analysis (max 300 words)\n"
    "- recommendations: Object with portfolio_modifier (string), sector_pref (list of sectors), notes (string)\n"
    "- evidence: Array of {claim, support} objects for key assertions\n\n"
    "Respond with JSON ONLY, no markdown, no code blocks."
)


def prepare_llm_prompt(text: str, max_tokens: int = 5000) -> str:
    """
    Prepare and sanitize LLM prompt.
    
    Trim text to token limit and escape special characters.
    
    Args:
        text: Input text to analyze
        max_tokens: Approximate token limit (rough: 1 token ≈ 4 chars)
    
    Returns:
        Formatted prompt
    """
    char_limit = max_tokens * 4
    if len(text) > char_limit:
        text = text[:char_limit] + "\n[...truncated...]"
        logger.info(f"Trimmed text to ~{max_tokens} tokens")
    
    # Escape quotes to avoid breaking JSON
    text = text.replace('"', '\\"').replace('\n', ' ')
    
    prompt = LLM_USER_PROMPT_TEMPLATE.format(corpus=text)
    return prompt

import requests
import json
import re
import logging
from typing import Dict, Any, Tuple, Optional

# Setup basic logging
logger = logging.getLogger(__name__)

# --- Model Configuration ---
# FIXED: Using the model you requested
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
BASE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def auto_format_text(text: str) -> str:
    """
    Automatically find and format chemical formulas and simple math notations.
    """
    if not text:
        return ""
    # Use str.maketrans for efficient subscripting
    subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    # Format chemical formulas like H2O
    text = re.sub(r"([A-Z][a-z]*)(\d+)", lambda m: m.group(1) + m.group(2).translate(subscripts), text)
    # Format simple exponents like x^2
    text = re.sub(r"(\w)\^(\-?[\d\.]+)", r"$\1^{\2}$", text)
    return text

def _call_gemini_api(api_key: str, user_prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Private function to send a request to the Gemini API.
    
    Args:
        api_key: The Google Gemini API key.
        user_prompt: The user's input prompt.
        system_prompt: The optional system-level instructions.
        
    Returns:
        A dictionary of the JSON response from the API.
    """
    # Construct the correct URL for the specified model
    gemini_api_url = f"{BASE_API_URL}/{MODEL_NAME}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}]
    }
    
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        
    logger.info(f"Calling Gemini API with system prompt: {bool(system_prompt)}")
    
    try:
        response = requests.post(gemini_api_url, headers=headers, json=payload, timeout=30)
        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Network or API Error: {e}")
        return {"error": f"❌ Network or API Error: {e}"}
        
    return response.json()

def extract_text_and_metrics(response_json: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts the generated text and usage metadata from a Gemini response.
    """
    if "error" in response_json:
        return response_json["error"], {}
        
    try:
        # Navigate the response structure safely
        text = response_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        logger.warning(f"Could not parse text from response: {response_json}")
        text = "⚠️ Could not parse response text."
        
    try:
        usage = response_json.get("usageMetadata", {})
        metrics = {
            "prompt_tokens": usage.get("promptTokenCount", 0),
            "completion_tokens": usage.get("candidatesTokenCount", 0),
            "total_tokens": usage.get("totalTokenCount", 0),
            "character_length": len(text),
            "finish_reason": response_json.get("candidates", [{}])[0].get("finishReason", "N/A"),
        }
    except Exception as e:
        logger.error(f"Error extracting metrics: {e}")
        metrics = {}
        
    return text, metrics

def calculate_insights(metrics_a: Dict, metrics_b: Dict) -> Optional[Dict]:
    """
    Analyzes the metrics and provides a dictionary of comparisons.
    This is pure calculation, no Streamlit code.
    """
    if not metrics_a or not metrics_b or metrics_b.get("total_tokens", 0) == 0:
        return None # Not enough data to compare

    try:
        insights = {}
        
        # Total Tokens
        token_delta = metrics_b["total_tokens"] - metrics_a["total_tokens"]
        token_percent_change = (token_delta / metrics_a["total_tokens"]) * 100 if metrics_a["total_tokens"] else 0
        insights["token_metric"] = (f"{token_delta:+} tokens", f"{token_percent_change:.1f}%")
        
        # Character Length
        len_delta = metrics_b["character_length"] - metrics_a["character_length"]
        len_percent_change = (len_delta / metrics_a["character_length"]) * 100 if metrics_a["character_length"] else 0
        insights["length_metric"] = (f"{len_delta:+} chars", f"{len_percent_change:.1f}%")
        
        # Completion Tokens
        comp_token_delta = metrics_b["completion_tokens"] - metrics_a["completion_tokens"]
        comp_percent_change = (comp_token_delta / metrics_a["completion_tokens"]) * 100 if metrics_a["completion_tokens"] else 0
        insights["completion_metric"] = (f"{comp_token_delta:+} tokens", f"{comp_percent_change:.1f}%")

        # --- Textual Summary ---
        summary = []
        if len_percent_change > 5:
            summary.append(f"The system prompt produced a **significantly more detailed** response (+{len_percent_change:.1f}% longer).")
        elif len_percent_change < -5:
            summary.append(f"The system prompt resulted in a **more concise** response ({len_percent_change:.1f}% shorter).")
        else:
            summary.append("The response lengths were **very similar**.")
        
        if token_percent_change > 0:
            summary.append(f"This came at a cost of **{token_percent_change:.1f}% more tokens**.")
        else:
            summary.append(f"This was achieved while being **more token-efficient** ({token_percent_change:.1f}% fewer tokens).")
        insights["summary"] = " ".join(summary)
        
        # --- Verdict ---
        if len_percent_change > 5 and token_percent_change < 15:
            insights["verdict_type"] = "success"
            insights["verdict_text"] = "**🏆 The System Prompt appears better.** It provided a more detailed answer without a disproportionate increase in cost."
        elif token_percent_change > 15 and len_percent_change < token_percent_change:
            insights["verdict_type"] = "warning"
            insights["verdict_text"] = "**⚠️ The System Prompt is more expensive.** It used significantly more tokens for a modest increase in detail. Consider refining the system prompt."
        elif len_percent_change < -5:
            insights["verdict_type"] = "info"
            insights["verdict_text"] = "**💡 The System Prompt is more concise.** This is ideal if your goal is brevity and lower cost."
        else:
            insights["verdict_type"] = "info"
            insights["verdict_text"] = "**⚖️ The results are comparable.** The system prompt did not drastically change the output's size or cost."
            
        return insights
        
    except Exception as e:
        logger.error(f"Error calculating insights: {e}")
        return None

# --- Main Orchestration Function ---
def run_comparison(api_key: str, user_prompt: str, system_prompt: str) -> Dict[str, Any]:
    """
    The main function called by the frontend.
    Orchestrates the API calls and data extraction.
    """
    
    # API Call A: User-Only
    response_a_json = _call_gemini_api(api_key, user_prompt)
    response_a_text, metrics_a = extract_text_and_metrics(response_a_json)
    
    # API Call B: System+User
    if system_prompt:
        response_b_json = _call_gemini_api(api_key, user_prompt, system_prompt)
        response_b_text, metrics_b = extract_text_and_metrics(response_b_json)
    else:
        response_b_json = {}
        response_b_text = "⚠️ No system prompt provided."
        metrics_b = {}

    # Calculate insights
    insights = calculate_insights(metrics_a, metrics_b)

    return {
        "text_a": response_a_text,
        "metrics_a": metrics_a,
        "json_a": response_a_json,
        "text_b": response_b_text,
        "metrics_b": metrics_b,
        "json_b": response_b_json,
        "insights": insights
    }
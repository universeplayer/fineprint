"""Core contract analysis engine powered by LLM."""

from __future__ import annotations

import json
import os

from openai import OpenAI
from pydantic import ValidationError

from contractguard.models import AnalysisResult
from contractguard.prompts import get_prompts


DEFAULT_MODEL = "anthropic/claude-sonnet-4"
MAX_CONTRACT_CHARS = 120_000  # ~30K tokens


def get_client(
    api_key: str | None = None,
    base_url: str | None = None,
) -> OpenAI:
    """Create an OpenAI-compatible client."""
    api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    base_url = base_url or os.environ.get("OPENAI_BASE_URL") or os.environ.get(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )

    if not api_key:
        raise ValueError(
            "No API key found. Set one of:\n"
            "  export OPENROUTER_API_KEY=sk-or-...\n"
            "  export OPENAI_API_KEY=sk-...\n"
            "Or pass --api-key to the CLI."
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def analyze_contract(
    contract_text: str,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    base_url: str | None = None,
    lang: str = "en",
) -> AnalysisResult:
    """Analyze a contract and return structured results.

    Args:
        contract_text: The full text of the contract.
        model: The LLM model to use (OpenRouter model ID).
        api_key: API key for the LLM provider.
        base_url: Base URL for the LLM API.

    Returns:
        AnalysisResult with red flags, warnings, and fairness score.
    """
    if len(contract_text.strip()) < 50:
        raise ValueError("Contract text is too short. Please provide a complete document.")

    # Truncate if too long
    if len(contract_text) > MAX_CONTRACT_CHARS:
        contract_text = contract_text[:MAX_CONTRACT_CHARS] + "\n\n[... document truncated ...]"

    client = get_client(api_key=api_key, base_url=base_url)
    system_prompt, analysis_prompt = get_prompts(lang)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": analysis_prompt.format(contract_text=contract_text)},
        ],
        temperature=0.1,
        max_tokens=4096,
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown code block if present
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        content = "\n".join(lines)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse LLM response as JSON: {e}\n"
            f"Raw response:\n{content[:500]}"
        )

    try:
        return AnalysisResult(**data)
    except ValidationError as e:
        raise RuntimeError(f"LLM response did not match expected schema: {e}")

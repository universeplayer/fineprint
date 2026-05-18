"""ContractGuard as a Bindu A2A agent.

Wraps `contractguard.analyzer.analyze_contract()` in a Bindu handler so the
analyzer is reachable as a networked, DID-identified microservice over the
A2A JSON-RPC protocol. Peers send either:

  - a `text` part with the raw contract text, or
  - a `file` part with a base64-encoded PDF / DOCX / TXT / MD,

and get back the structured `AnalysisResult` (red flags, warnings,
protections, fairness score) as JSON.

Run:

    export OPENROUTER_API_KEY=sk-or-...
    pip install -e .
    pip install bindu
    python examples/bindu/agent.py

Agent card:  http://localhost:3773/.well-known/agent.json
DID doc:     http://localhost:3773/.well-known/did.json
JSON-RPC:    POST http://localhost:3773/   (method: message/send)
"""

from __future__ import annotations

import base64
import io
import json
import os
import tempfile
from pathlib import Path

from bindu.penguin.bindufy import bindufy

from contractguard.analyzer import DEFAULT_MODEL, analyze_contract
from contractguard.parser import extract_text

# Map MIME types we accept to the suffix `contractguard.parser.extract_text`
# expects. The parser dispatches off the file suffix, so we materialise file
# bytes to a temp file with the right extension and let the existing
# pdfplumber / python-docx code paths do their thing.
MIME_TO_SUFFIX = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "application/rtf": ".rtf",
    "text/rtf": ".rtf",
}


def _decode_file_part(part: dict) -> tuple[bytes, str]:
    """Return (file_bytes, mime_type) for a file part. Raises on malformed input."""
    file_info = part.get("file") or {}
    payload = file_info.get("bytes") or file_info.get("data")
    if not payload:
        raise ValueError("file part is missing 'bytes' / 'data'")
    file_bytes = base64.b64decode(payload) if isinstance(payload, str) else payload
    mime_type = file_info.get("mimeType") or ""
    return file_bytes, mime_type


def _extract_from_file_part(part: dict) -> str:
    file_bytes, mime_type = _decode_file_part(part)
    suffix = MIME_TO_SUFFIX.get(mime_type)
    if not suffix:
        raise ValueError(
            f"unsupported mimeType {mime_type!r}; expected one of {sorted(MIME_TO_SUFFIX)}"
        )
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as fh:
        fh.write(file_bytes)
        tmp_path = Path(fh.name)
    try:
        return extract_text(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _collect_inputs(messages: list[dict]) -> tuple[str | None, str]:
    """Walk A2A messages and return (prompt, contract_text).

    `prompt` is currently informational (the analyzer doesn't take a free-form
    prompt — the schema is fixed), but we surface it in the response so callers
    can pass through their own context for downstream agents in a chain.
    `contract_text` is the concatenated content of all text-after-prompt and
    file parts found across user messages.
    """
    prompt: str | None = None
    text_chunks: list[str] = []
    text_part_count = 0

    for msg in messages or []:
        role = msg.get("role")
        if role is not None and role != "user":
            continue
        for part in msg.get("parts") or []:
            kind = part.get("kind")
            if kind == "text":
                text = part.get("text") or ""
                text_part_count += 1
                # First text part is treated as a prompt (e.g. "review this
                # lease"). Subsequent text parts are appended as contract text
                # — lets callers paste the contract inline without a file
                # upload.
                if text_part_count == 1 and len(text) < 500:
                    prompt = text.strip() or None
                else:
                    text_chunks.append(text)
            elif kind == "file":
                try:
                    text_chunks.append(_extract_from_file_part(part))
                except Exception as exc:  # noqa: BLE001 — surfaced to caller below
                    text_chunks.append(f"[file part error: {exc}]")

    return prompt, "\n\n".join(c for c in text_chunks if c)


def handler(messages: list[dict]) -> str:
    """A2A handler: extract contract → analyse → return JSON string.

    Returning a `str` keeps the manifest worker happy; we encode the structured
    `AnalysisResult` as JSON so peers can `JSON.parse()` it on the wire. The
    agent card surfaces that the agent emits structured output (see config
    below).
    """
    prompt, contract_text = _collect_inputs(messages)

    if not contract_text or len(contract_text.strip()) < 50:
        return json.dumps(
            {
                "error": "no_contract",
                "message": (
                    "Send the contract as a `text` part (>= 50 chars) or as a "
                    "`file` part with mimeType pdf / docx / txt / md / rtf."
                ),
            }
        )

    model = os.environ.get("CONTRACTGUARD_MODEL", DEFAULT_MODEL)
    lang = os.environ.get("CONTRACTGUARD_LANG", "en")

    try:
        result = analyze_contract(contract_text=contract_text, model=model, lang=lang)
    except Exception as exc:  # noqa: BLE001 — propagate to caller as structured error
        return json.dumps({"error": "analysis_failed", "message": str(exc)})

    payload = result.model_dump(mode="json")
    if prompt:
        payload["prompt"] = prompt
    return json.dumps(payload)


config = {
    "author": os.environ.get("CONTRACTGUARD_AUTHOR", "contractguard@example.com"),
    "name": "contractguard",
    "description": (
        "AI contract review agent. Sends a PDF/DOCX/TXT contract or raw text "
        "and returns structured red flags, warnings, protections, and a "
        "fairness score (0-100, A+ to F)."
    ),
    "deployment": {
        "url": "http://localhost:3773",
        "expose": True,
        "cors_origins": ["http://localhost:5173", "http://localhost:3000"],
    },
    # Pay-per-scan via x402 (USDC on Base Sepolia). Uncomment and fill in a
    # pay-to address to charge peers per analysis. Leave commented for free /
    # local development.
    #
    # "execution_cost": {
    #     "amount": "0.10",
    #     "token": "USDC",
    #     "network": "base-sepolia",
    #     "pay_to_address": "0xYOUR_ADDRESS_HERE",
    # },
    "enable_system_message": False,
}


if __name__ == "__main__":
    bindufy(config, handler)

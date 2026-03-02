<div align="center">

# ContractGuard

**AI-powered contract review agent — never sign a bad contract again.**

Upload any contract → get red flags, unfair terms, and plain-English explanations in seconds.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/universeplayer/ContractGuard/actions/workflows/ci.yml/badge.svg)](https://github.com/universeplayer/ContractGuard/actions)

**[English](README.md) | [中文](README_CN.md)**

</div>

---

## The Problem

You're about to sign a lease, NDA, or employment contract. The document is 15 pages of dense legal text. You have two options:

1. **Pay a lawyer $300-500/hour** to review it
2. **Hope for the best** and sign blindly

Most people choose option 2. **ContractGuard** gives you option 3:

```bash
contractguard scan my-lease.pdf
```

```
✔ Parsed my-lease.pdf (4,521 characters)

⬤ RED FLAGS (5 found)
==================================================

  1. Non-refundable security deposit
     Clause: Section 3
     "The security deposit is non-refundable and shall
      be retained by Landlord upon termination"
     Most states require deposits to be refundable.
     This clause is likely illegal in California.
     Suggestion: Remove "non-refundable" language.

  2. Unlimited landlord access without notice
     Clause: Section 5
     "Landlord shall have the right to enter the Property
      at any time, with or without notice"
     California law requires 24-hour written notice.
     Suggestion: Add "with 24 hours written notice"

  3. Tenant pays for structural repairs
     ...

⚠ WARNINGS (3 found)
==================================================
  ...

✔ PROTECTIONS (2 found)
==================================================
  ...

FAIRNESS SCORE: D (28/100)
  5 red flags  3 warnings  2 protections  4 missing
```

## Quick Start

### Installation

```bash
pip install contractguard
```

### Set up your API key

ContractGuard works with any OpenAI-compatible API. The easiest way is [OpenRouter](https://openrouter.ai/) (supports Claude, GPT-4, DeepSeek, etc.):

```bash
export OPENROUTER_API_KEY=sk-or-...
```

Or use OpenAI directly:
```bash
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1
```

### Scan a contract

```bash
# Scan a PDF lease
contractguard scan lease.pdf

# Scan a Word document
contractguard scan contract.docx

# Scan a text file
contractguard scan nda.txt

# Use a specific model
contractguard scan contract.pdf --model openai/gpt-4o

# Save report as markdown
contractguard scan contract.pdf -o report.md

# Get raw JSON output
contractguard scan contract.pdf --json
```

### Python API

```python
from contractguard.analyzer import analyze_contract
from contractguard.parser import extract_text

text = extract_text("my-lease.pdf")
result = analyze_contract(text)

print(f"Fairness: {result.fairness_grade} ({result.fairness_score}/100)")
for flag in result.red_flags:
    print(f"RED FLAG - {flag.title}: {flag.explanation}")
```

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based PDFs (scanned PDFs need `--ocr`) |
| Word | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| Markdown | `.md` | Markdown files |

## Supported Contract Types

ContractGuard automatically detects the contract type and adjusts its analysis:

- **Residential Leases** — rent, deposits, maintenance, access rights
- **NDAs** — scope, duration, non-compete clauses
- **Employment Contracts** — non-compete, IP assignment, termination
- **Freelance/Contractor Agreements** — payment terms, IP ownership
- **SaaS Terms of Service** — data ownership, liability, auto-renewal
- **Loan Agreements** — interest rates, prepayment penalties, default terms
- **Purchase Agreements** — warranties, returns, dispute resolution

## How It Works

1. **Parse** — Extract text from PDF, DOCX, or TXT files
2. **Detect** — Automatically identify the contract type
3. **Analyze** — AI agent reviews every clause for:
   - Red flags (serious issues that could harm you)
   - Warnings (concerns worth discussing)
   - Good protections (clauses that protect you)
   - Missing protections (standard clauses not present)
4. **Score** — Generate a fairness grade (A+ to F)
5. **Report** — Beautiful terminal output or markdown export

## Configuration

### Using different LLM providers

```bash
# OpenRouter (default) - access to 100+ models
export OPENROUTER_API_KEY=sk-or-...
contractguard scan contract.pdf --model anthropic/claude-sonnet-4

# OpenAI
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1
contractguard scan contract.pdf --model gpt-4o

# Local models (Ollama) — your data never leaves your machine
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
contractguard scan contract.pdf --model llama3.1
```

## Try it with the sample contracts

```bash
# Clone the repo
git clone https://github.com/universeplayer/ContractGuard.git
cd ContractGuard

# Install
pip install -e .

# Scan the sample lease (intentionally has many red flags)
export OPENROUTER_API_KEY=sk-or-...
contractguard scan examples/sample_lease.txt

# Scan the sample NDA
contractguard scan examples/sample_nda.txt
```

## FAQ

**Is this legal advice?**
No. ContractGuard is an educational tool that helps you understand contract terms. Always consult a qualified attorney for legal advice.

**Is my contract data sent to the cloud?**
The contract text is sent to the LLM provider you configure (OpenRouter, OpenAI, etc.). For maximum privacy, use a local model via Ollama.

**How accurate is it?**
ContractGuard uses state-of-the-art LLMs (Claude, GPT-4) which are highly capable at legal text analysis. However, it may miss nuances that a human lawyer would catch. Think of it as a first-pass filter, not a replacement for legal counsel.

**What languages are supported?**
ContractGuard works with contracts in any language supported by the underlying LLM. English contracts produce the best results.

## Contributing

Contributions are welcome! Please open an issue or submit a PR.

## License

[MIT](LICENSE) — use it however you want.

---

<div align="center">

**If ContractGuard saved you from a bad contract, consider giving it a star!**

[Report a Bug](https://github.com/universeplayer/ContractGuard/issues) · [Request a Feature](https://github.com/universeplayer/ContractGuard/issues)

</div>

<div align="center">

# 🔍 fineprint

**AI agent that reads the fine print so you don't have to.**

Upload any contract → get red flags, unfair terms, and plain-English explanations in seconds.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/universeplayer/fineprint/actions/workflows/ci.yml/badge.svg)](https://github.com/universeplayer/fineprint/actions)

**[English](README.md) | [中文](README_CN.md)**

</div>

---

## The Problem

You're about to sign a lease, NDA, or employment contract. The document is 15 pages of dense legal text. You have two options:

1. **Pay a lawyer $300-500/hour** to review it
2. **Hope for the best** and sign blindly

Most people choose option 2. **fineprint** gives you option 3:

```bash
fineprint scan my-lease.pdf
```

```
✔ Parsed my-lease.pdf (4,521 characters)

┌────────────────────────────────────────┐
│  FINEPRINT Contract Analysis Report    │
│  Contract Type: LEASE                  │
└────────────────────────────────────────┘

╭─ Summary ───────────────────────────────────────────╮
│ A 12-month residential lease with several           │
│ one-sided clauses that heavily favor the landlord.   │
│ Multiple provisions may be unenforceable under       │
│ California tenant protection laws.                   │
╰─────────────────────────────────────────────────────╯

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

╭─ FAIRNESS SCORE ──────────────────────────────────╮
│  ████████████░░░░░░░░░░░░░░  D  (28/100)          │
│                                                     │
│  5 red flags  3 warnings  2 protections  4 missing │
╰─────────────────────────────────────────────────────╯
```

## Quick Start

### Installation

```bash
pip install fineprint-ai
```

### Set up your API key

fineprint works with any OpenAI-compatible API. The easiest way is [OpenRouter](https://openrouter.ai/) (supports Claude, GPT-4, DeepSeek, etc.):

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
fineprint scan lease.pdf

# Scan a Word document
fineprint scan contract.docx

# Scan a text file
fineprint scan nda.txt

# Use a specific model
fineprint scan contract.pdf --model openai/gpt-4o

# Save report as markdown
fineprint scan contract.pdf -o report.md

# Get raw JSON output
fineprint scan contract.pdf --json
```

### Python API

```python
from fineprint.analyzer import analyze_contract
from fineprint.parser import extract_text

text = extract_text("my-lease.pdf")
result = analyze_contract(text)

print(f"Fairness: {result.fairness_grade} ({result.fairness_score}/100)")
for flag in result.red_flags:
    print(f"🔴 {flag.title}: {flag.explanation}")
```

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based PDFs (scanned PDFs need `--ocr`) |
| Word | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| Markdown | `.md` | Markdown files |

## Supported Contract Types

fineprint automatically detects the contract type and adjusts its analysis:

- 🏠 **Residential Leases** — rent, deposits, maintenance, access rights
- 📝 **NDAs** — scope, duration, non-compete clauses
- 💼 **Employment Contracts** — non-compete, IP assignment, termination
- 🤝 **Freelance/Contractor Agreements** — payment terms, IP ownership
- 📱 **SaaS Terms of Service** — data ownership, liability, auto-renewal
- 💰 **Loan Agreements** — interest rates, prepayment penalties, default terms
- 🛒 **Purchase Agreements** — warranties, returns, dispute resolution

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
fineprint scan contract.pdf --model anthropic/claude-sonnet-4

# OpenAI
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1
fineprint scan contract.pdf --model gpt-4o

# Local models (Ollama)
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
fineprint scan contract.pdf --model llama3.1
```

## Try it with the sample contracts

```bash
# Clone the repo
git clone https://github.com/universeplayer/fineprint.git
cd fineprint

# Install
pip install -e .

# Scan the sample lease (intentionally has many red flags)
export OPENROUTER_API_KEY=sk-or-...
fineprint scan examples/sample_lease.txt

# Scan the sample NDA
fineprint scan examples/sample_nda.txt
```

## FAQ

**Is this legal advice?**
No. fineprint is an educational tool that helps you understand contract terms. Always consult a qualified attorney for legal advice.

**Is my contract data sent to the cloud?**
The contract text is sent to the LLM provider you configure (OpenRouter, OpenAI, etc.). For maximum privacy, use a local model via Ollama.

**How accurate is it?**
fineprint uses state-of-the-art LLMs (Claude, GPT-4) which are highly capable at legal text analysis. However, it may miss nuances that a human lawyer would catch. Think of it as a first-pass filter, not a replacement for legal counsel.

**What languages are supported?**
fineprint works with contracts in any language supported by the underlying LLM. English contracts produce the best results.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) — use it however you want.

---

<div align="center">

**If fineprint saved you from a bad contract, consider giving it a ⭐**

[Report a Bug](https://github.com/universeplayer/fineprint/issues) · [Request a Feature](https://github.com/universeplayer/fineprint/issues)

</div>

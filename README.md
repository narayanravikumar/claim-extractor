# claim-extractor

Extracts structured claim data from insurance claim PDFs. A teaching
project (Month 1 of a six-month FDE prep plan), not a production service
and not aimed at real users.

## What it does

A single endpoint takes an uploaded PDF, extracts its text layer, and
calls an LLM to turn that text into a `ClaimDocument`: claimant name,
date of loss, and optionally policy number, claim type, and amount
claimed. See `docs/decisons/` for the reasoning behind the schema, the
API boundaries, and the LLM extraction/failure strategy.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=sk-...   # only needed to actually call the model
```

## Run

```bash
uvicorn claim_extractor.main:app --reload
```

## Use

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -F "file=@/path/to/claim.pdf"
```

Responses:

| Status | Meaning |
|---|---|
| 200 | A validated `ClaimDocument` |
| 400 | The upload is not a PDF (checked by magic number, not filename) |
| 422 | The PDF has no readable text layer (e.g. a scanned image) |
| 502 | The model's reply could not be turned into a valid `ClaimDocument` |

## Test

```bash
pytest
```

## Status

Month 1 engineering floor: API boundary, schema, extraction call, and
failure handling are done and tested. No eval set for extraction
accuracy exists yet; ADR 003 covers what is and isn't decided about
that. Next up is Month 2 (retrieval) on a separate, real project.

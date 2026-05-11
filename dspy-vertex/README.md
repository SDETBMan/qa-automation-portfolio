# DSPy Bug Severity Classifier — Vertex AI Variant

Demonstrates the same DSPy BootstrapFewShot optimization pipeline as `dspy-optimizer`, but using **Google Vertex AI (Gemini 1.5 Flash)** as the LLM backend instead of OpenAI.

## Why This Exists

This variant proves that the DSPy optimization pipeline is cloud-portable. The classifier, datasets, and optimizer logic are identical — only the LLM configuration changes. This demonstrates:

- **Cloud-native ML pipeline** skills (Vertex AI / GCP)
- **Backend portability** — same optimization, different provider
- **Graceful degradation** — exits cleanly when GCP credentials are unavailable

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # edit with your GCP project
python run.py --mode baseline
```

## Comparison with dspy-optimizer

| Aspect | dspy-optimizer | dspy-vertex |
|--------|---------------|-------------|
| LLM Backend | OpenAI GPT-4o-mini | Vertex AI Gemini 1.5 Flash |
| Classifier | BugClassifier (identical) | BugClassifier (identical) |
| Optimizer | BootstrapFewShot (identical) | BootstrapFewShot (identical) |
| Dataset | 30 bug reports (identical) | 30 bug reports (identical) |
| Auth | OPENAI_API_KEY | GCP_PROJECT + gcloud auth |

## Modes

- `--mode baseline` — Zero-shot classification (no few-shot examples)
- `--mode optimized` — BootstrapFewShot compilation + evaluation
- `--mode compare` — Side-by-side accuracy comparison

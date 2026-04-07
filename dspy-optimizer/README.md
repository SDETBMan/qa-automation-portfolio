# dspy-optimizer — Bug Report Severity Classifier

> **Stack:** DSPy 2.6 · `dspy.ChainOfThought` · `BootstrapFewShot` · OpenAI `gpt-4o-mini`

A systematic prompt optimization demo that classifies bug reports by severity (Critical / High / Medium / Low) and compares zero-shot baseline accuracy against a BootstrapFewShot-optimized classifier.

---

## What it demonstrates

| Concept | Where |
|---|---|
| **DSPy Signatures** | `classifier/signatures.py` — `InputField` / `OutputField` with docstring instructions |
| **ChainOfThought module** | `classifier/modules.py` — reasoning before classification |
| **BootstrapFewShot optimizer** | `classifier/optimizer.py` — auto-selects few-shot demos from trainset |
| **Before/after accuracy** | `run.py --mode compare` — prints delta on 10-item held-out split |
| **Offline dataset** | `datasets/bug_reports.py` — 30 hardcoded examples, zero API cost |
| **Compiled program export** | `output/compiled_classifier.json` — saved after optimization |

---

## Quick start

```bash
cd dspy-optimizer
pip install -r requirements.txt

# Add your OpenAI key
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...

# Side-by-side baseline vs optimized (default)
python run.py

# Zero-shot only
python run.py --mode baseline

# Bootstrap + evaluate only
python run.py --mode optimized
```

---

## Key DSPy patterns

```python
# Signature — declarative I/O spec
class BugSeveritySignature(dspy.Signature):
    """Classify a software bug report into a severity level. ..."""
    report: str = dspy.InputField(desc="Bug report text.")
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning.")
    severity: str = dspy.OutputField(desc="One of: Critical, High, Medium, Low.")

# Module — wraps ChainOfThought
class BugClassifier(dspy.Module):
    def __init__(self):
        self.classify = dspy.ChainOfThought(BugSeveritySignature)
    def forward(self, report):
        return self.classify(report=report)

# Optimizer
optimizer = BootstrapFewShot(metric=severity_metric, max_bootstrapped_demos=3)
compiled = optimizer.compile(BugClassifier(), trainset=TRAINSET)
```

---

## Dataset

The 30-item synthetic dataset (`datasets/bug_reports.py`) is hardcoded — no API call needed to generate it, zero cost, works fully offline. Distribution: 7 Critical · 7 High · 8 Medium · 8 Low.

Split: first 20 → trainset, last 10 → held-out devset.

---

## File layout

```
dspy-optimizer/
├── run.py                      # CLI: --mode baseline|optimized|compare
├── requirements.txt
├── .env.example                # OPENAI_API_KEY template
├── classifier/
│   ├── signatures.py           # BugSeveritySignature
│   ├── modules.py              # BugClassifier(dspy.Module)
│   └── optimizer.py            # compile_with_bootstrap(), evaluate()
├── datasets/
│   └── bug_reports.py          # 30 synthetic dspy.Example items
└── output/
    └── compiled_classifier.json  # saved after --mode optimized (git-ignored)
```

---

## Cost

| Step | Model | Est. calls | Est. cost |
|---|---|---|---|
| Baseline eval (10 items) | `gpt-4o-mini` | 10 | ~$0.002 |
| BootstrapFewShot compile (20 items) | `gpt-4o-mini` | ~40 | ~$0.015 |
| Optimized eval (10 items) | `gpt-4o-mini` | 10 | ~$0.002 |
| **Total (compare mode)** | | **~60** | **~$0.02** |

Production upgrade path: replace `BootstrapFewShot` with `MIPROv2` for joint optimization of instructions + demonstrations (higher accuracy, ~$0.10–0.50 per run).

Auto-recharge is disabled — this runs only on `workflow_dispatch` in CI.

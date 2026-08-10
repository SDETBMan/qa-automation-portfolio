# Re-exported from dspy-optimizer — single source of truth for shared classifier logic.
# dspy-vertex differs only in LM backend configuration (Vertex AI vs OpenAI).
import sys
from pathlib import Path

_OPTIMIZER_DIR = str(Path(__file__).resolve().parent.parent.parent / "dspy-optimizer")
if _OPTIMIZER_DIR not in sys.path:
    sys.path.insert(0, _OPTIMIZER_DIR)

from classifier.modules import BugClassifier  # noqa: E402

__all__ = ["BugClassifier"]

# Re-exported from dspy-optimizer — single source of truth for shared classifier logic.
import sys
from pathlib import Path

_OPTIMIZER_DIR = str(Path(__file__).resolve().parent.parent.parent / "dspy-optimizer")
if _OPTIMIZER_DIR not in sys.path:
    sys.path.insert(0, _OPTIMIZER_DIR)

from classifier.signatures import BugSeveritySignature  # noqa: E402

__all__ = ["BugSeveritySignature"]

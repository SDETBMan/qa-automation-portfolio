# Re-exported from dspy-optimizer — single source of truth for shared datasets.
import sys
from pathlib import Path

_OPTIMIZER_DIR = str(Path(__file__).resolve().parent.parent.parent / "dspy-optimizer")
if _OPTIMIZER_DIR not in sys.path:
    sys.path.insert(0, _OPTIMIZER_DIR)

from datasets.bug_reports import DATASET, DEVSET, TRAINSET  # noqa: E402

__all__ = ["DATASET", "DEVSET", "TRAINSET"]

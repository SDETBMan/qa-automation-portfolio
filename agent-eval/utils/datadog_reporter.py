# Re-exported from ai-eval — single source of truth for shared DataDog reporting.
import sys
from pathlib import Path

_AI_EVAL_DIR = str(Path(__file__).resolve().parent.parent.parent / "ai-eval")
if _AI_EVAL_DIR not in sys.path:
    sys.path.insert(0, _AI_EVAL_DIR)

from utils.datadog_reporter import (  # noqa: E402
    send_eval_score,
    send_test_metrics,
)

__all__ = ["send_eval_score", "send_test_metrics"]

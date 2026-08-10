# Re-exported from ai-eval — single source of truth for shared DataDog reporting.
# Uses importlib file-path loading to avoid circular import (same module name).
import importlib.util
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent.parent / "ai-eval" / "utils" / "datadog_reporter.py"
_spec = importlib.util.spec_from_file_location("_ai_eval_datadog_reporter", _SRC)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

send_eval_score = _mod.send_eval_score
send_test_metrics = _mod.send_test_metrics

__all__ = ["send_eval_score", "send_test_metrics"]

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "social_live_smoke.py"
SPEC = importlib.util.spec_from_file_location("ssswet_social_live_smoke", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_live_smoke_passes_only_when_all_provider_requests_succeed():
    assert MODULE.smoke_exit_code(12, 0) == 0
    assert MODULE.smoke_exit_code(4, 0) == 0


def test_live_smoke_fails_on_partial_or_total_provider_outages():
    assert MODULE.smoke_exit_code(11, 1) == 1
    assert MODULE.smoke_exit_code(1, 11) == 1
    assert MODULE.smoke_exit_code(0, 12) == 1


def test_live_smoke_rejects_impossible_negative_request_counts():
    import pytest

    with pytest.raises(ValueError, match="cannot be negative"):
        MODULE.smoke_exit_code(-1, 0)
    with pytest.raises(ValueError, match="cannot be negative"):
        MODULE.smoke_exit_code(1, -1)

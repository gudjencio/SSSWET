#!/usr/bin/env python3
"""Run the public web accessibility and static asset budget gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core"))

from ssswet_core.web_quality_gate import audit_web_root

report = audit_web_root(ROOT / "web")
print(json.dumps({
    "passed": report["passed"],
    "measurements": report["measurements"],
    "budgets": report["budgets"],
    "page_issue_counts": {item["page"]: item["accessibility_issue_count"] for item in report["pages"]},
    "failures": report["failures"],
}, ensure_ascii=False, indent=2))
if not report["passed"]:
    raise SystemExit(1)

"""Guard the Node 24-compatible action pins used by CI and scheduled checks."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {
    ".github/workflows/ci.yml": ("actions/checkout", "actions/setup-python", "actions/setup-node"),
    ".github/workflows/core-tests.yml": ("actions/checkout", "actions/setup-python"),
    ".github/workflows/hourly-regression-watch.yml": ("actions/checkout", "actions/setup-python", "actions/setup-node"),
    ".github/workflows/regression-watch-30m.yml": ("actions/checkout", "actions/setup-python", "actions/setup-node", "actions/github-script"),
}
PINS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",  # v7.0.1, node24
    "actions/setup-python": "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",  # v7.1.0, node24
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1",  # v7.1.0, node24
    "actions/github-script": "ed597411d8f924073f98dfc5c65a23a2325f34cd",  # v8.0.0, node24
}


def test_ci_and_scheduled_workflows_pin_node24_actions():
    for workflow, actions in WORKFLOWS.items():
        content = (ROOT / workflow).read_text(encoding="utf-8")
        for action in actions:
            expected = PINS[action]
            pattern = rf"^\s*uses:\s*{re.escape(action)}@{expected}(?:\s+#.*)?$"
            assert re.search(pattern, content, re.MULTILINE), f"{workflow} must pin {action} to its verified Node 24 release"
        if "actions/setup-node" in actions:
            assert re.search(r"^\s*package-manager-cache:\s*false\s*$", content, re.MULTILINE), f"{workflow} must disable unused Node package-manager caching"

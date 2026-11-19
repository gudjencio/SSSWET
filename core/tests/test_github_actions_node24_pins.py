"""Guard Node 24-compatible action pins across CI, schedules, Pages and release workflows."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {
    ".github/workflows/ci.yml": ("actions/checkout", "actions/setup-python", "actions/setup-node"),
    ".github/workflows/core-tests.yml": ("actions/checkout", "actions/setup-python"),
    ".github/workflows/hourly-regression-watch.yml": ("actions/checkout", "actions/setup-python", "actions/setup-node"),
    ".github/workflows/regression-watch-30m.yml": ("actions/checkout", "actions/setup-python", "actions/setup-node", "actions/github-script"),
    ".github/workflows/pages-deploy.yml": ("actions/checkout", "actions/upload-pages-artifact", "actions/deploy-pages"),
    ".github/workflows/process-public-reports.yml": ("actions/checkout", "actions/setup-python"),
    ".github/workflows/release-apps.yml": (
        "actions/checkout",
        "actions/setup-node",
        "actions/setup-java",
        "actions/upload-artifact",
        "actions/download-artifact",
        "softprops/action-gh-release",
    ),
}
PINS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",  # v7.0.1, node24
    "actions/setup-python": "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",  # v7.1.0, node24
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1",  # v7.1.0, node24
    "actions/github-script": "ed597411d8f924073f98dfc5c65a23a2325f34cd",  # v8.0.0, node24
    "actions/upload-pages-artifact": "fc324d3547104276b827a68afc52ff2a11cc49c9",  # v5.0.0, uploads artifact v7
    "actions/deploy-pages": "368f82528645a54fb793d4d04e342629a3f51346",  # v5.0.1, node24
    "actions/setup-java": "dded0888837ed1f317902acf8a20df0ad188d165",  # v5.0.0, node24
    "actions/upload-artifact": "bbbca2ddaa5d8feaa63e36b76fdaad77386f024f",  # v7.0.0, node24
    "actions/download-artifact": "37930b1c2abaa49bbe596cd826c3c89aef350131",  # v7.0.0, node24
    "softprops/action-gh-release": "efb35369e0ad2afab669f228072c1b0d510eae64",  # v3.0.3, node24
}


def test_all_active_ci_and_side_effect_workflows_pin_node24_actions():
    for workflow, actions in WORKFLOWS.items():
        content = (ROOT / workflow).read_text(encoding="utf-8")
        for action in actions:
            expected = PINS[action]
            pattern = rf"^\s*(?:-\s*)?uses:\s*{re.escape(action)}@{expected}(?:\s+#.*)?$"
            assert re.search(pattern, content, re.MULTILINE), f"{workflow} must pin {action} to its verified Node 24 release"
        if "actions/setup-node" in actions:
            assert re.search(r"^\s*package-manager-cache:\s*false\s*$", content, re.MULTILINE), f"{workflow} must disable unused Node package-manager caching"


def test_release_workflow_keeps_build_permissions_read_only_and_publish_tag_only():
    content = (ROOT / ".github/workflows/release-apps.yml").read_text(encoding="utf-8")
    workflow_permissions = content.split("jobs:", 1)[0]
    assert re.search(r"(?m)^permissions:\n  contents: read$", workflow_permissions)
    assert "contents: write" not in workflow_permissions

    release = re.search(r"(?ms)^  release:(.*)\Z", content)
    assert release is not None
    assert "if: startsWith(github.ref, 'refs/tags/v')" in release.group(1)
    assert re.search(r"(?m)^    permissions:\n      contents: write$", release.group(1))
    assert re.search(r"(?m)^  pull_request:\n    paths:$", workflow_permissions)
    assert content.count("persist-credentials: false") == 2

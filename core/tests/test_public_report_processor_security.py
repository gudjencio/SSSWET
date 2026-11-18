"""Security regression tests for the public-report automation patch gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "process_public_report.py"
WORKFLOW = ROOT / ".github" / "workflows" / "process-public-reports.yml"


@pytest.fixture
def processor(monkeypatch):
    monkeypatch.setenv("GITHUB_REPOSITORY", "gudjencio/SSSWET")
    monkeypatch.setenv("ISSUE_NUMBER", "1")
    monkeypatch.setenv("GH_TOKEN", "test-token-not-real")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    spec = importlib.util.spec_from_file_location("ssswet_public_report_processor", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_patch(path: str) -> str:
    return (
        f"diff --git a/{path} b/{path}\n"
        "index 1111111..2222222 100644\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        "@@ -1 +1 @@\n"
        "-old\n"
        "+new\n"
    )


def test_patch_gate_accepts_small_existing_file_changes(processor):
    path = "core/ssswet_core/example.py"
    assert processor.validate_patch(make_patch(path)) == [(path, path)]


def test_patch_gate_rejects_paths_outside_the_allowlist(processor):
    path = ".github/workflows/ci.yml"
    assert processor.validate_patch(make_patch(path)) is None


def test_patch_gate_rejects_unmatched_unified_diff_paths(processor):
    patch = make_patch("core/tests/example.py").replace(
        "+++ b/core/tests/example.py", "+++ b/.github/workflows/ci.yml"
    )
    assert processor.validate_patch(patch) is None


@pytest.mark.parametrize(
    "path",
    [
        "web/donation-config.js",
        "web/product-purchase-config.js",
        "web/platform-downloads.js",
        "docs/MONTHLY_TECHNOLOGY_FINANCING.md",
        "docs/PUBLICATION_POLICY.md",
        "docs/POLICY.md",
        "docs/LEGAL_POLICY.md",
        "docs/CONTRIBUTIONS.md",
        "docs/APP_DISTRIBUTION.md",
    ],
)
def test_automatic_patch_allowlist_excludes_financial_legal_and_availability_files(processor, path):
    assert not processor.allowed(path)
    assert processor.validate_patch(make_patch(path)) is None


def test_patch_gate_rejects_file_creation_deletion_and_mode_changes(processor):
    path = "core/tests/example.py"
    assert processor.validate_patch(make_patch(path).replace(
        "index 1111111..2222222 100644", "new file mode 100644\nindex 1111111..2222222 100644"
    )) is None
    assert processor.validate_patch(make_patch(path).replace(
        "index 1111111..2222222 100644", "deleted file mode 100644\nindex 1111111..2222222 100644"
    )) is None
    assert processor.validate_patch(make_patch(path).replace(
        "index 1111111..2222222 100644", "old mode 100644\nnew mode 100755\nindex 1111111..2222222 100644"
    )) is None


def test_validation_environment_strips_credentials_but_keeps_required_tools(processor):
    source = {
        "PATH": "/usr/bin",
        "GITHUB_API_URL": "https://api.github.com",
        "SAFE_SETTING": "kept",
        "GH_TOKEN": "secret",
        "OPENAI_API_KEY": "secret",
        "GITHUB_TOKEN": "secret",
        "AWS_ACCESS_KEY_ID": "secret",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "secret",
        "GIT_CONFIG_VALUE_0": "secret",
        "SSH_AUTH_SOCK": "/tmp/agent.sock",
    }
    clean = processor.validation_environment(source)
    assert clean == {
        "PATH": "/usr/bin",
        "GITHUB_API_URL": "https://api.github.com",
        "SAFE_SETTING": "kept",
    }


def test_context_reader_never_follows_symlinks_outside_repository(processor, tmp_path):
    root = tmp_path / "repo"
    inside = root / "core" / "tests" / "linked.md"
    outside = tmp_path / "private.txt"
    inside.parent.mkdir(parents=True)
    outside.write_text("must not be read", encoding="utf-8")
    inside.symlink_to(outside)
    processor.ROOT = root
    assert processor.safe_context_path(inside) is None
    regular = inside.parent / "normal.md"
    regular.write_text("allowed context", encoding="utf-8")
    assert processor.safe_context_path(regular) == regular.resolve()


def test_report_processor_checkout_does_not_persist_credentials_and_auth_is_set_after_tests():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    checkout = re.search(
        r"uses:\s*actions/checkout@[^\n]+\n\s*with:\n(?P<settings>(?:\s+[^\n]+\n?)+)",
        workflow,
    )
    assert checkout and re.search(r"persist-credentials:\s*false", checkout.group("settings"))
    assert script.index('run(["gh","auth","setup-git"])') < script.index('run(["git","push","origin",branch])')

"""Security regression tests for the separated public-report patch pipeline."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import re
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / ".github" / "scripts"
SCRIPT = SCRIPT_DIR / "process_public_report.py"
WORKFLOW = ROOT / ".github" / "workflows" / "process-public-reports.yml"
sys.path.insert(0, str(SCRIPT_DIR))


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


def test_patch_gate_rejects_paths_outside_allowlist(processor):
    assert processor.validate_patch(make_patch(".github/workflows/ci.yml")) is None


def test_patch_gate_rejects_mismatched_unified_diff_paths(processor):
    patch = make_patch("core/tests/example.py").replace(
        "+++ b/core/tests/example.py", "+++ b/.github/workflows/ci.yml"
    )
    assert processor.validate_patch(patch) is None


@pytest.mark.parametrize(
    "path",
    [
        "web/donation-config.js",
        "web/product-purchase-config.js",
        "web/product-availability.js",
        "web/platform-downloads.js",
        "docs/MONTHLY_TECHNOLOGY_FINANCING.md",
        "docs/PUBLICATION_POLICY.md",
        "docs/POLICY.md",
        "docs/LEGAL_POLICY.md",
        "docs/CONTRIBUTIONS.md",
        "docs/APP_DISTRIBUTION.md",
        "docs/tax-refund.md",
        "core/ssswet_core/payment_model.py",
    ],
)
def test_automatic_patch_scope_excludes_sensitive_files(processor, path):
    assert not processor.allowed(path)
    assert processor.validate_patch(make_patch(path)) is None


def test_patch_gate_rejects_creation_deletion_mode_change_and_binary_patches(processor):
    path = "core/tests/example.py"
    patch = make_patch(path)
    assert processor.validate_patch(patch.replace(
        "index 1111111..2222222 100644", "new file mode 100644\nindex 1111111..2222222 100644"
    )) is None
    assert processor.validate_patch(patch.replace(
        "index 1111111..2222222 100644", "deleted file mode 100644\nindex 1111111..2222222 100644"
    )) is None
    assert processor.validate_patch(patch.replace(
        "index 1111111..2222222 100644", "old mode 100644\nnew mode 100755\nindex 1111111..2222222 100644"
    )) is None
    assert processor.validate_patch(patch.replace(
        "@@ -1 +1 @@\n", "GIT binary patch\n@@ -1 +1 @@\n"
    )) is None


def test_existing_test_files_may_only_receive_additions(processor):
    path = "core/tests/test_example.py"
    assert processor.validate_patch(make_patch(path)) is None
    addition = make_patch(path).replace("-old\n", " context\n")
    assert processor.validate_patch(addition) == [(path, path)]


def test_patch_gate_rejects_duplicate_paths(processor):
    assert processor.validate_patch(make_patch("docs/example.md") + make_patch("docs/example.md")) is None


def test_validation_environment_removes_credentials(processor):
    from public_report_patch_guard import validation_environment
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
    assert validation_environment(source) == {
        "PATH": "/usr/bin",
        "GITHUB_API_URL": "https://api.github.com",
        "SAFE_SETTING": "kept",
    }


def test_context_reader_never_follows_symlinks_outside_repository(processor, tmp_path):
    from public_report_patch_guard import safe_context_path
    root = tmp_path / "repo"
    inside = root / "core" / "tests" / "linked.md"
    outside = tmp_path / "private.txt"
    inside.parent.mkdir(parents=True)
    outside.write_text("must not be read", encoding="utf-8")
    inside.symlink_to(outside)
    assert safe_context_path(inside, root) is None
    regular = inside.parent / "normal.md"
    regular.write_text("allowed context", encoding="utf-8")
    assert safe_context_path(regular, root) == regular.resolve()


def test_workflow_separates_secret_bearing_prepare_and_publish_from_validation():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    prepare = re.search(r"(?ms)^  prepare_report:(.*?)(?=^  validate_report:)", workflow).group(1)
    validate = re.search(r"(?ms)^  validate_report:(.*?)(?=^  publish_report:)", workflow).group(1)
    publish = re.search(r"(?ms)^  publish_report:(.*)\Z", workflow).group(1)
    assert "OPENAI_API_KEY" in prepare and "GH_TOKEN" in prepare
    assert "OPENAI_API_KEY" not in validate and "GH_TOKEN" not in validate
    assert "permissions:\n      contents: read" in validate
    assert "validate_public_report_patch.py" in validate
    assert "pytest" not in prepare and "pytest" not in publish
    assert "publish_public_report_patch.py" in publish and "GH_TOKEN" in publish
    for job in (prepare, validate, publish):
        assert "persist-credentials: false" in job


def test_processor_only_prepares_patch_and_never_executes_or_publishes():
    script = SCRIPT.read_text(encoding="utf-8")
    assert "pytest" not in script
    assert "git push" not in script
    assert "gh pr create" not in script


def test_publisher_does_not_run_tests():
    publisher = (SCRIPT_DIR / "publish_public_report_patch.py").read_text(encoding="utf-8")
    assert "pytest" not in publisher
    assert '"gh", "pr", "create"' in publisher


def test_processor_does_not_emit_duplicate_default_job_outputs():
    script = SCRIPT.read_text(encoding="utf-8")
    assert "emit_outputs(False)" not in script

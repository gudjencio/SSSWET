#!/usr/bin/env python3
"""Publish a previously validated public-report patch; this job never executes it."""
from __future__ import annotations
import base64
import os
import subprocess
from pathlib import Path

from public_report_patch_guard import validate_patch, MAX_PATCH_BYTES

ROOT = Path(__file__).resolve().parents[2]


def run(command, cwd=ROOT, env=None):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True, env=env)


def main():
    patch = base64.b64decode(os.environ["REPORT_PATCH_B64"], validate=True).decode("utf-8")
    if len(patch.encode("utf-8")) > MAX_PATCH_BYTES:
        raise SystemExit("Patch exceeds maximum size")
    pairs = validate_patch(patch)
    if not pairs:
        raise SystemExit("Patch failed the scope guard")
    patch_path = ROOT / ".ssswet-report-publish.patch"
    patch_path.write_text(patch, encoding="utf-8")
    try:
        run(["git", "apply", "--check", str(patch_path)])
        run(["git", "apply", str(patch_path)])
    finally:
        patch_path.unlink(missing_ok=True)

    issue = int(os.environ["ISSUE_NUMBER"])
    run_id = int(os.environ["GITHUB_RUN_ID"])
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
    branch = f"auto/public-report-{issue}-{run_id}-{attempt}"
    run(["git", "config", "user.name", "ssswet-report-bot"])
    run(["git", "config", "user.email", "ssswet-report-bot@users.noreply.github.com"])
    run(["git", "add", "--", *[new for _, new in pairs]])
    run(["git", "commit", "-m", f"Improve project from public report #{issue}"])
    run(["git", "checkout", "-b", branch])
    run(["gh", "auth", "setup-git"])
    run(["git", "push", "--set-upstream", "origin", branch])
    body = (
        f"Closes #{issue}\n\nThis bounded patch was validated in a separate credential-free job. "
        "The publishing job did not execute the generated code. Maintainer review is required before merge."
    )
    pr = run(["gh", "pr", "create", "--title", f"Automated improvement for report #{issue}", "--body", body, "--base", "main", "--head", branch])
    run(["gh", "issue", "comment", str(issue), "--body", "A scoped patch passed credential-free validation and was opened for maintainer review: " + pr.stdout.strip()])
    print(pr.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate generated public-report patches in a separate credential-free job."""
from __future__ import annotations
import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from public_report_patch_guard import validate_patch, validation_environment, MAX_PATCH_BYTES

ROOT = Path(__file__).resolve().parents[2]


def run(command, cwd=ROOT, env=None):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True, env=env)
    if result.stdout:
        print(result.stdout[-4000:])
    if result.stderr:
        print(result.stderr[-4000:])
    return result


def main():
    encoded = os.environ.get("REPORT_PATCH_B64", "")
    if not encoded:
        raise SystemExit("No generated patch was supplied")
    try:
        patch = base64.b64decode(encoded, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise SystemExit(f"Patch output is not valid UTF-8 base64: {type(exc).__name__}")
    if len(patch.encode("utf-8")) > MAX_PATCH_BYTES or not validate_patch(patch):
        raise SystemExit("Patch failed the scope guard")
    env = validation_environment()
    with tempfile.TemporaryDirectory(prefix="ssswet-report-validation-") as tmp:
        env["HOME"] = tmp
        env["TMPDIR"] = tmp
        patch_path = Path(tmp) / "candidate.patch"
        patch_path.write_text(patch, encoding="utf-8")
        run(["git", "apply", "--check", str(patch_path)], env=env)
        run(["git", "apply", str(patch_path)], env=env)
        baseline = run(["git", "diff", "--binary"], env=env).stdout
        run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT / "core", env=env)
        for js in sorted((ROOT / "web").glob("*.js")):
            run(["node", "--check", str(js)], env=env)
        run(["node", "web/test-locales.cjs"], env=env)
        after = run(["git", "diff", "--binary"], env=env).stdout
        if baseline != after:
            raise SystemExit("Validation tests modified tracked files; patch was rejected")
    print("Public-report patch validation passed in a separate credential-free job.")


if __name__ == "__main__":
    raise SystemExit(main())

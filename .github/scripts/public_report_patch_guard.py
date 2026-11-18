"""Strict, non-executing scope guard for public-report generated diffs."""
from __future__ import annotations
import re
from pathlib import Path

MAX_PATCH_BYTES = 100_000
MAX_FILES = 6
PREFIXES = ("web/", "docs/", "core/ssswet_core/", "core/tests/")
ROOT_FILES = {"README.md"}
SUFFIXES = {".py", ".js", ".css", ".html", ".md", ".json", ".yml", ".yaml", ".toml"}
SENSITIVE_PATH_PATTERN = re.compile(
    r"(?i)(?:^|[/_.-])(?:payments?|donations?|subscriptions?|refunds?|tax|billing|finance|financing|financial|legal|polic(?:y|ies)|customers?|product[-_]purchase|product[-_]availability|platform[-_]downloads?|version[-_]center|app[-_]distribution|releases?|downloads?|contributions?)(?:$|[/_.-])"
)
SENSITIVE_ENV_PATTERN = re.compile(
    r"(?i)(?:token|secret|password|passwd|api_key|access_key|private_key|credential|authorization|cookie|(?:^|_)pat(?:$|_))"
)


def allowed(path: str) -> bool:
    """Allow only bounded edits to public code, docs, tests, or README."""
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    path = path.strip()
    parts = path.split("/")
    if path.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        return False
    if SENSITIVE_PATH_PATTERN.search(path):
        return False
    if path in ROOT_FILES:
        return True
    return path.startswith(PREFIXES) and Path(path).suffix.lower() in SUFFIXES and not path.startswith(".github/")


def validate_patch(patch: object) -> list[tuple[str, str]] | None:
    """Validate a small diff touching existing files only; test changes must be additive."""
    if not isinstance(patch, str) or not patch.startswith("diff --git "):
        return None
    if len(patch.encode("utf-8")) > MAX_PATCH_BYTES or "\x00" in patch:
        return None
    sections = [section for section in re.split(r"(?m)(?=^diff --git )", patch) if section.strip()]
    if not sections or len(sections) > MAX_FILES:
        return None
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    forbidden = re.compile(
        r"(?m)^(?:new file mode|deleted file mode|old mode|new mode|rename from|rename to|copy from|copy to|GIT binary patch|Binary files )"
    )
    for section in sections:
        lines = section.splitlines()
        if not lines:
            return None
        header = re.fullmatch(r"diff --git a/([^\s]+) b/([^\s]+)", lines[0])
        if not header:
            return None
        old, new = header.groups()
        if old != new or not allowed(new) or new in seen:
            return None
        seen.add(new)
        hunk_start = next((i for i, line in enumerate(lines) if line.startswith("@@ ")), None)
        if hunk_start is None:
            return None
        header_lines = lines[:hunk_start]
        if forbidden.search("\n".join(header_lines)):
            return None
        file_headers = [line for line in header_lines if line.startswith("--- ") or line.startswith("+++ ")]
        if len(file_headers) != 2:
            return None
        old_header = re.fullmatch(r"--- a/([^\t ]+)(?:\t.*)?", file_headers[0])
        new_header = re.fullmatch(r"\+\+\+ b/([^\t ]+)(?:\t.*)?", file_headers[1])
        if not old_header or not new_header or old_header.group(1) != old or new_header.group(1) != new:
            return None
        if new.startswith("core/tests/") and any(line.startswith("-") for line in lines[hunk_start:]):
            return None
        pairs.append((old, new))
    return pairs or None


def validation_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    """Return a credential-free environment for test execution (defense in depth)."""
    import os
    source = dict(os.environ if source is None else source)
    return {
        key: value for key, value in source.items()
        if not SENSITIVE_ENV_PATTERN.search(key)
        and not key.upper().startswith(("GIT_CONFIG", "ACTIONS_ID_TOKEN_"))
        and key.upper() not in {"GIT_ASKPASS", "SSH_AUTH_SOCK"}
    }


def safe_context_path(path: Path, root: Path) -> Path | None:
    """Reject symlinks and paths resolving outside the repository or edit scope."""
    try:
        if path.is_symlink():
            return None
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(root.resolve(strict=True)).as_posix()
    except (OSError, ValueError):
        return None
    if not allowed(relative) or not resolved.is_file():
        return None
    return resolved

"""Small deterministic validators shared by opt-in research assurance utilities."""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("value must be finite and JSON serializable") from exc


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def text(value: Any, field: str, maximum: int, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"{field} must be text of at most {maximum} characters")
    result = value.strip()
    if not result and not allow_empty:
        raise ValueError(f"{field} must not be empty")
    if any(ord(ch) < 32 and ch not in "\\t\\n\\r" for ch in result):
        raise ValueError(f"{field} contains control characters")
    return result


def identifier(value: Any, field: str, maximum: int = 200) -> str:
    result = text(value, field, maximum)
    if any(ord(ch) < 32 for ch in result):
        raise ValueError(f"{field} contains control characters")
    return result


def aware_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a timezone-aware ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be a timezone-aware ISO timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must be a timezone-aware ISO timestamp")
    return parsed.astimezone(timezone.utc)


def sha256_hex(value: Any, field: str) -> str:
    result = text(value, field, 64).lower()
    if not re.fullmatch(r"[a-f0-9]{64}", result):
        raise ValueError(f"{field} must be a SHA-256 hex digest")
    return result


def finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{field} must be a finite number")
    return float(value)

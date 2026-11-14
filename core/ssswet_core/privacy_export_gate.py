"""Local-only privacy redaction preview for text considered for public export."""
from __future__ import annotations
import hashlib
import re
from .assurance_common import text

MAX_TEXT = 20_000
_PATTERNS = [
    ("email", re.compile(r"(?i)(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])")),
    ("secret_like_value", re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*[\"']?([A-Za-z0-9_./+=-]{8,})")),
    ("ipv4_address", re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")),
    ("phone_like", re.compile(r"(?<!\w)(?:\+\d{1,3}[ .()-]?)?\d{1,4}(?:[ .()-]\d{1,4}){2,5}(?!\w)")),
    ("coordinates", re.compile(r"(?i)\b(?:lat(?:itude)?\s*[:=]\s*[-+]?\d{1,2}(?:\.\d+)?\s*[,;]\s*(?:lon(?:gitude)?\s*[:=]\s*)[-+]?\d{1,3}(?:\.\d+)?)")),
]


def scan_and_redact(text_value: str) -> dict:
    original = text(text_value, "text", MAX_TEXT, allow_empty=True)
    candidates = []
    for kind, pattern in _PATTERNS:
        for match in pattern.finditer(original):
            start, end = match.span()
            if kind == "ipv4_address":
                octets = [int(part) for part in match.group(0).split(".")]
                if any(part > 255 for part in octets):
                    continue
            if kind == "coordinates":
                numbers = re.findall(r"[-+]?\d+(?:\.\d+)?", match.group(0))
                if len(numbers) >= 2 and (abs(float(numbers[0])) > 90 or abs(float(numbers[1])) > 180):
                    continue
            candidates.append((start, end, kind))
    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))
    selected, cursor = [], -1
    for item in candidates:
        if item[0] >= cursor:
            selected.append(item)
            cursor = item[1]
    output, findings, cursor = [], [], 0
    for start, end, kind in selected:
        output.append(original[cursor:start])
        output.append(f"[REDACTED:{kind.upper()}]")
        findings.append({"type": kind, "start": start, "end": end})
        cursor = end
    output.append(original[cursor:])
    redacted = "".join(output)
    return {"redacted_text": redacted, "original_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(), "redacted_sha256": hashlib.sha256(redacted.encode("utf-8")).hexdigest(), "finding_count": len(findings), "findings": findings, "matched_values_returned": False, "human_review_required": True, "publication_authorized": False, "scanner_is_privacy_guarantee": False}

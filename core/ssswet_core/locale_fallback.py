"""Deterministic BCP-47 locale fallback without automatic translation."""
from __future__ import annotations
import re

_TAG = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")
_RTL_LANGUAGES = {"ar", "arc", "ckb", "dv", "fa", "he", "nqo", "ps", "sd", "ug", "ur", "yi"}
_RTL_SCRIPTS = {"Adlm", "Arab", "Aran", "Hebr", "Hatr", "Mand", "Mend", "Merc", "Mero", "Nkoo", "Palm", "Phlp", "Phnx", "Prti", "Rohg", "Samr", "Syrc", "Thaa"}
_LTR_SCRIPTS = {"Beng", "Cyrl", "Deva", "Ethi", "Geor", "Grek", "Guru", "Hans", "Hant", "Jpan", "Kore", "Latn", "Mlym", "Orya", "Sinh", "Taml", "Telu", "Thai"}

def canonicalize_locale(tag: str) -> str:
    if not isinstance(tag, str):
        raise ValueError("locale must be a valid, simple BCP-47 language tag")
    normalized = tag.strip().replace("_", "-")
    if not _TAG.fullmatch(normalized):
        raise ValueError("locale must be a valid, simple BCP-47 language tag")
    parts = normalized.split("-")
    if not re.fullmatch(r"[A-Za-z]{2,8}", parts[0]):
        raise ValueError("invalid language subtag")
    canonical = [parts[0].lower()]
    for part in parts[1:]:
        if len(part) == 4 and part.isalpha():
            canonical.append(part.title())
        elif (len(part) == 2 and part.isalpha()) or (len(part) == 3 and part.isdigit()):
            canonical.append(part.upper())
        else:
            canonical.append(part.lower())
    return "-".join(canonical)

def _direction(tag: str) -> tuple[str, str]:
    parts = tag.split("-")
    script = next((part for part in parts[1:] if len(part) == 4 and part.isalpha()), None)
    if script in _RTL_SCRIPTS:
        return "rtl", "explicit_rtl_script"
    if script in _LTR_SCRIPTS:
        return "ltr", "explicit_ltr_script"
    language = parts[0]
    if language in _RTL_LANGUAGES:
        return "rtl", "language_default"
    return "ltr", "language_default"

def resolve_locale(requested: str, available: list[str], *, fallback: str = "en") -> dict:
    if not isinstance(available, list) or not available or len(available) > 500:
        raise ValueError("available must contain 1 to 500 locale tags")
    canonical_available = []
    for item in available:
        canonical = canonicalize_locale(item)
        if canonical not in canonical_available:
            canonical_available.append(canonical)
    canonical_fallback = canonicalize_locale(fallback)
    if canonical_fallback not in canonical_available:
        raise ValueError("fallback locale must be present in available")
    requested_tag = canonicalize_locale(requested)
    candidates = [requested_tag]
    parts = requested_tag.split("-")
    while len(parts) > 1:
        parts.pop()
        candidates.append("-".join(parts))
    resolved = next((candidate for candidate in candidates if candidate in canonical_available), canonical_fallback)
    direction, direction_source = _direction(resolved)
    return {
        "requested": requested_tag, "resolved": resolved, "fallback_used": resolved != requested_tag,
        "fallback_chain": candidates + ([canonical_fallback] if canonical_fallback not in candidates else []),
        "direction": direction, "direction_source": direction_source,
        "automatic_translation_performed": False, "translation_completeness_guaranteed": False,
    }

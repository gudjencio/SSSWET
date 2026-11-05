"""Translation catalogue coverage, placeholder parity and deterministic fallback."""
from __future__ import annotations

import re


_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}|\{\s*([A-Za-z0-9_.-]+)\s*\}")


def _placeholders(value: str) -> list[str]:
    found = []
    for match in _PLACEHOLDER.finditer(value):
        found.append(match.group(1) or match.group(2))
    return sorted(found)


def _language_chain(language: str, fallback_language: str) -> list[str]:
    requested = str(language or "").strip().replace("_", "-").casefold()
    fallback = str(fallback_language or "").strip().replace("_", "-").casefold()
    chain = []
    if requested:
        chain.append(requested)
        primary = requested.split("-", 1)[0]
        if primary not in chain:
            chain.append(primary)
    if fallback and fallback not in chain:
        chain.append(fallback)
    return chain


def audit_translation_catalogue(
    source: dict[str, str],
    translations: dict[str, dict[str, str]],
    *,
    fallback_language: str = "en",
) -> dict:
    if not isinstance(source, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in source.items()):
        raise ValueError("source catalogue must contain string keys and values")
    if not isinstance(translations, dict) or any(not isinstance(v, dict) for v in translations.values()):
        raise ValueError("translations must map language codes to catalogues")
    if fallback_language not in translations:
        raise ValueError("fallback language must exist")
    report = {}
    source_placeholders = {key: _placeholders(value) for key, value in source.items()}
    for language, catalogue in translations.items():
        missing = sorted(
            key for key in source
            if key not in catalogue or not isinstance(catalogue[key], str) or not catalogue[key].strip()
        )
        mismatches = []
        for key in sorted(set(source) & set(catalogue)):
            translated = catalogue[key]
            if not isinstance(translated, str) or not translated.strip():
                continue
            expected = source_placeholders[key]
            actual = _placeholders(translated)
            if expected != actual:
                mismatches.append({
                    "key": key,
                    "expected_placeholders": expected,
                    "actual_placeholders": actual,
                })
        report[language] = {
            "source_count": len(source),
            "translated_count": len(source) - len(missing),
            "coverage": (len(source) - len(missing)) / len(source) if source else 1.0,
            "missing": missing,
            "placeholder_mismatches": mismatches,
            "placeholder_mismatch_count": len(mismatches),
            "fallback": language == fallback_language,
        }
    return report


def resolve_translation(
    key: str,
    translations: dict[str, dict[str, str]],
    language: str,
    *,
    fallback_language: str = "en",
) -> dict:
    """Resolve exact locale, base language, then configured fallback without guessing."""
    if not isinstance(key, str) or not key:
        raise ValueError("translation key is required")
    if not isinstance(translations, dict):
        raise ValueError("translations must be a language-to-catalogue mapping")
    for candidate in _language_chain(language, fallback_language):
        catalogue = translations.get(candidate)
        if isinstance(catalogue, dict):
            value = catalogue.get(key)
            if isinstance(value, str) and value.strip():
                return {
                    "value": value,
                    "source_language": candidate,
                    "fallback_used": candidate != str(language or "").replace("_", "-").casefold(),
                    "missing": False,
                }
    return {"value": None, "source_language": None, "fallback_used": False, "missing": True}

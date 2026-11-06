"""Translation-catalogue coverage, placeholder and locale-direction checks."""
from __future__ import annotations
from collections import Counter
import re

MAX_SOURCE_KEYS = 10000
MAX_LOCALES = 200
_LOCALE_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.-]*)\}|%(?:\d+\$)?[sdif]")
_RTL_LANGUAGES = {"ar", "fa", "he", "ps", "sd", "ur", "yi"}


def _placeholders(value: str) -> Counter:
    return Counter(match.group(0) for match in _PLACEHOLDER_RE.finditer(value))


def audit_translation_catalogue(source: dict[str, str], translations: dict[str, dict[str, str]], *, fallback_language: str = "en") -> dict:
    if not isinstance(source, dict) or len(source) > MAX_SOURCE_KEYS or any(not isinstance(key, str) or not isinstance(value, str) for key, value in source.items()):
        raise ValueError(f"source must be a string-to-string dictionary of at most {MAX_SOURCE_KEYS} keys")
    if not isinstance(translations, dict) or len(translations) > MAX_LOCALES or fallback_language not in translations:
        raise ValueError(f"translations must include the fallback and contain at most {MAX_LOCALES} locales")
    report = {}
    source_placeholders = {key: _placeholders(value) for key, value in source.items()}
    for language, catalogue in sorted(translations.items()):
        if not isinstance(language, str) or not _LOCALE_RE.fullmatch(language):
            raise ValueError("language keys must be valid BCP 47-style locale tags")
        if not isinstance(catalogue, dict) or len(catalogue) > MAX_SOURCE_KEYS + 1000:
            raise ValueError("each translation catalogue must be an object with a bounded number of keys")
        if any(not isinstance(key, str) or not isinstance(value, str) for key, value in catalogue.items()):
            raise ValueError("translation keys and values must be strings")
        missing = sorted(key for key in source if key not in catalogue or not catalogue[key].strip())
        extras = sorted(key for key in catalogue if key not in source)
        mismatches, untranslated = [], []
        for key in sorted(set(source) & set(catalogue)):
            value = catalogue[key]
            if not value.strip():
                continue
            expected, actual = source_placeholders[key], _placeholders(value)
            if expected != actual:
                mismatches.append({"key": key, "expected": sorted(expected.elements()), "actual": sorted(actual.elements())})
            if language != fallback_language and value.strip().casefold() == source[key].strip().casefold():
                untranslated.append(key)
        translated_count = len(source) - len(missing)
        direction = "rtl" if language.split("-")[0].casefold() in _RTL_LANGUAGES else "ltr"
        report[language] = {
            "source_count": len(source), "translated_count": translated_count,
            "coverage": translated_count / len(source) if source else 1.0,
            "missing": missing, "extra_keys": extras, "placeholder_mismatches": mismatches,
            "possibly_untranslated": untranslated, "direction": direction,
            "locale_tag_valid": True,
            "quality_issue_count": len(missing) + len(extras) + len(mismatches) + len(untranslated),
            "fallback": language == fallback_language,
        }
    return {
        **report,
        "_meta": {
            "placeholder_check": "named braces and common printf placeholders",
            "translation_quality_human_review_required": True,
            "machine_translation_or_semantic_accuracy_established": False,
        },
    }

"""Conservative cross-language checks for scientific translation drift.

This utility compares supplied text; it does not translate, infer intent or
certify that a translation is semantically correct.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from decimal import Decimal, InvalidOperation

MAX_TEXT_CHARS = 20_000
MAX_TERM_PAIRS = 200

NEGATION_CUES = {
    "ar": ("لا", "ليس", "لم", "لن", "بدون"),
    "bn": ("না", "নয়", "নেই", "ছাড়া"),
    "cs": ("ne", "nikdy", "bez"),
    "da": ("ikke", "aldrig", "uden"),
    "de": ("nicht", "kein", "keine", "niemals", "ohne"),
    "el": ("δεν", "όχι", "χωρίς", "ποτέ"),
    "en": ("no", "not", "never", "without", "cannot", "can't", "neither", "none"),
    "es": ("no", "nunca", "sin", "ningún", "ninguna"),
    "fa": ("نه", "نیست", "بدون", "هرگز"),
    "fi": ("ei", "eivät", "ilman"),
    "fr": ("ne", "pas", "jamais", "sans", "aucun", "aucune", "ni"),
    "he": ("לא", "אין", "בלי", "מעולם לא"),
    "hi": ("नहीं", "मत", "बिना", "कभी नहीं"),
    "id": ("tidak", "bukan", "tanpa", "belum"),
    "it": ("non", "mai", "senza", "nessun"),
    "ja": ("ない", "ません", "ではない", "なし", "ないで"),
    "ko": ("않", "없다", "아니다", "못", "없이"),
    "nl": ("niet", "geen", "nooit", "zonder"),
    "pl": ("nie", "nigdy", "bez", "żaden"),
    "pt": ("não", "nunca", "sem", "nenhum"),
    "ro": ("nu", "niciodată", "fără"),
    "ru": ("не", "нет", "никогда", "без"),
    "sv": ("inte", "aldrig", "utan"),
    "th": ("ไม่", "ไม่มี", "มิได้"),
    "tr": ("değil", "yok", "asla", "olmadan"),
    "uk": ("не", "ні", "ніколи", "без"),
    "vi": ("không", "chẳng", "chưa", "không có"),
    "zh": ("不", "没有", "无", "未", "从不"),
}

_UNIT_ALIASES = {
    "%": "%", "percent": "%", "percentage": "%",
    "m": "m", "meter": "m", "meters": "m", "metre": "m", "metres": "m",
    "km": "km", "kilometer": "km", "kilometers": "km", "kilometre": "km", "kilometres": "km",
    "cm": "cm", "mm": "mm", "s": "s", "sec": "s", "second": "s", "seconds": "s",
    "ms": "ms", "millisecond": "ms", "milliseconds": "ms",
    "min": "min", "minute": "min", "minutes": "min", "h": "h", "hour": "h", "hours": "h",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg", "g": "g", "gram": "g", "grams": "g",
    "mg": "mg", "l": "L", "liter": "L", "litre": "L", "ml": "mL",
    "hz": "Hz", "khz": "kHz", "mhz": "MHz", "ghz": "GHz",
    "w": "W", "kw": "kW", "mw": "MW", "j": "J", "kj": "kJ", "mj": "MJ",
    "n": "N", "kn": "kN", "pa": "Pa", "kpa": "kPa", "mpa": "MPa",
    "v": "V", "a": "A", "k": "K", "°c": "°C", "°f": "°F",
    "m/s": "m/s", "km/h": "km/h", "m²": "m²", "m^2": "m²", "m³": "m³", "m^3": "m³",
    "db": "dB", "ppm": "ppm", "mol": "mol", "ev": "eV", "kev": "keV", "mev": "MeV", "gev": "GeV",
}
_NUMBER = re.compile(r"(?<![\w])([+-]?\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?)(?![\w])", re.UNICODE)
_UNIT_AFTER = re.compile(r"^\s*(%|°[CF]|[A-Za-zµμΩ]{1,5}(?:/[A-Za-zµμΩ]{1,5})?|m[²³]?)")


def _clean_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT_CHARS:
        raise ValueError(f"{field} must contain 1 to {MAX_TEXT_CHARS} characters")
    return value


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _number_key(raw: str) -> str:
    try:
        return format(Decimal(raw.replace(",", ".")).normalize(), "f")
    except InvalidOperation:
        return raw


def _quantities(value: str) -> Counter:
    found = Counter()
    for match in _NUMBER.finditer(value):
        number = _number_key(match.group(1))
        tail = value[match.end():match.end() + 24]
        unit_match = _UNIT_AFTER.match(tail)
        unit = ""
        if unit_match:
            candidate = unit_match.group(1).casefold()
            unit = _UNIT_ALIASES.get(candidate, "")
        found[(number, unit)] += 1
    return found


def _negation_present(value: str, language: str | None) -> tuple[bool, list[str]]:
    normalized = _normalize(value)
    codes = [language.split("-")[0].lower()] if language else sorted(NEGATION_CUES)
    cues = []
    for code in codes:
        if code not in NEGATION_CUES:
            raise ValueError(f"unsupported language for negation audit: {code}")
        for phrase in NEGATION_CUES[code]:
            if phrase.casefold() in normalized:
                cues.append({"language": code, "cue": phrase})
    return bool(cues), cues


def audit_translation(
    original: str,
    translated: str,
    *,
    source_language: str | None = None,
    target_language: str | None = None,
    term_pairs: list[dict] | None = None,
) -> dict:
    original = _clean_text(original, "original")
    translated = _clean_text(translated, "translated")
    for language in (source_language, target_language):
        if language is not None and (not isinstance(language, str) or not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", language.lower())):
            raise ValueError("language values must be BCP-47-like tags")
    if term_pairs is None:
        term_pairs = []
    if not isinstance(term_pairs, list) or len(term_pairs) > MAX_TERM_PAIRS:
        raise ValueError(f"term_pairs must be a list of at most {MAX_TERM_PAIRS}")
    missing_terms = []
    for pair in term_pairs:
        if not isinstance(pair, dict):
            raise ValueError("each term pair must be an object")
        source_term = _clean_text(pair.get("source"), "term_pairs.source")
        target_term = _clean_text(pair.get("translation"), "term_pairs.translation")
        if _normalize(source_term) not in _normalize(original):
            missing_terms.append({"side": "original", "term": source_term})
        if _normalize(target_term) not in _normalize(translated):
            missing_terms.append({"side": "translated", "term": target_term})
    source_quantities, target_quantities = _quantities(original), _quantities(translated)
    missing_quantities = list((source_quantities - target_quantities).elements())
    added_quantities = list((target_quantities - source_quantities).elements())
    source_negation, source_cues = _negation_present(original, source_language)
    target_negation, target_cues = _negation_present(translated, target_language)
    negation_mismatch = source_negation != target_negation
    mismatches = []
    if missing_quantities:
        mismatches.append("quantity_missing_or_changed_in_translation")
    if added_quantities:
        mismatches.append("quantity_added_or_changed_in_translation")
    if missing_terms:
        mismatches.append("configured_critical_term_missing")
    if negation_mismatch:
        mismatches.append("negation_presence_differs")
    return {
        "source_language": source_language,
        "target_language": target_language,
        "original_text": original,
        "translated_text": translated,
        "quantity_pairs_in_original": sorted([list(item) for item in source_quantities.elements()]),
        "quantity_pairs_in_translation": sorted([list(item) for item in target_quantities.elements()]),
        "quantities_missing_from_translation": missing_quantities,
        "quantities_added_in_translation": added_quantities,
        "missing_critical_terms": missing_terms,
        "original_negation_detected": source_negation,
        "translated_negation_detected": target_negation,
        "original_negation_cues": source_cues,
        "translated_negation_cues": target_cues,
        "mismatch_codes": mismatches,
        "review_required": bool(mismatches),
        "translation_performed": False,
        "translation_correctness_certified": False,
        "scientific_evidence_status_changed": False,
        "limitations": [
            "Lexical checks cannot determine negation scope, modality, sarcasm or semantic equivalence.",
            "Unit aliases are finite; unrecognized unit spellings may not be compared.",
            "A clean report is not proof that the translation is faithful.",
        ],
    }

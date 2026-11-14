"""Heuristic translation-integrity checks for numbers, units, negation and protected terms."""
from __future__ import annotations
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from .assurance_common import text

MAX_TEXT = 20_000
_NEGATION = {
    "en": ("not", "no", "never", "without", "cannot", "none"),
    "fr": ("ne", "pas", "non", "sans", "jamais", "aucun", "aucune"),
    "es": ("no", "nunca", "sin", "ningun", "ninguna"),
    "de": ("nicht", "kein", "keine", "ohne", "nie"),
    "it": ("non", "mai", "senza", "nessun"),
    "pt": ("não", "nunca", "sem", "nenhum"),
    "nl": ("niet", "geen", "zonder", "nooit"),
    "ja": ("ない", "ません", "無", "不", "否定"),
    "ko": ("않", "없", "아니", "못"),
    "zh": ("不", "无", "沒有", "没有", "未"),
    "ru": ("не", "нет", "никогда", "без"),
}
_UNITS = ("mm", "cm", "km", "kg", "mg", "ms", "min", "mpa", "kpa", "pa", "kn", "nm", "hz", "db", "ppm", "kw", "kwh", "mw", "°c", "°f", "°", "m", "g", "s", "h", "n", "j", "w", "v", "a", "l", "ml")
_NUMBER_RE = re.compile(r"(?<![\\w])[-+]?\\d+(?:[.,]\\d+)?%?(?![\\w])")
_NUMBER_UNIT_RE = re.compile(r"(?<![\\w])[-+]?\\d+(?:[.,]\\d+)?%?\\s*(" + "|".join(re.escape(x) for x in sorted(set(_UNITS), key=len, reverse=True)) + r")(?![\\w])", re.IGNORECASE)


def _language(value: str, field: str) -> str:
    code = text(value, field, 20).lower().split("-")[0]
    if code not in _NEGATION:
        raise ValueError(f"{field} is not supported by the integrity cue set")
    return code


def _number_token(value: str) -> str:
    raw = value.replace("%", "")
    if "," in raw and "." not in raw:
        left, right = raw.rsplit(",", 1)
        raw = left + ("." + right if len(right) <= 2 else right)
    else:
        raw = raw.replace(",", "")
    try:
        number = Decimal(raw)
        normalized = format(number.normalize(), "f")
        if normalized in {"-0", ""}:
            normalized = "0"
        return normalized + ("%" if value.endswith("%") else "")
    except (InvalidOperation, ValueError):
        return value


def _has_negation(value: str, language: str) -> bool:
    if language in {"ja", "ko", "zh"}:
        return any(cue in value for cue in _NEGATION[language])
    return any(re.search(r"(?<!\\w)" + re.escape(cue) + r"(?!\\w)", value, re.UNICODE) for cue in _NEGATION[language])


def audit_translation_integrity(original_text: str, translated_text: str, *, source_language: str, target_language: str, protected_terms: list[str] | tuple[str, ...] = ()) -> dict:
    original = text(original_text, "original_text", MAX_TEXT)
    translated = text(translated_text, "translated_text", MAX_TEXT)
    source = _language(source_language, "source_language")
    target = _language(target_language, "target_language")
    if source == target:
        raise ValueError("source_language and target_language must differ")
    if not isinstance(protected_terms, (list, tuple)) or len(protected_terms) > 100:
        raise ValueError("protected_terms must contain at most 100 entries")
    terms = [text(term, "protected_term", 200) for term in protected_terms]
    original_numbers = [_number_token(item) for item in _NUMBER_RE.findall(original)]
    translated_numbers = [_number_token(item) for item in _NUMBER_RE.findall(translated)]
    original_units = [item.casefold() for item in _NUMBER_UNIT_RE.findall(original)]
    translated_units = [item.casefold() for item in _NUMBER_UNIT_RE.findall(translated)]
    original_fold = unicodedata.normalize("NFKC", original).casefold()
    translated_fold = unicodedata.normalize("NFKC", translated).casefold()
    source_negation = _has_negation(original_fold, source)
    target_negation = _has_negation(translated_fold, target)
    missing_terms = [term for term in terms if unicodedata.normalize("NFKC", term).casefold() not in translated_fold]
    flags = []
    if original_numbers != translated_numbers:
        flags.append("numeric_tokens_differ")
    if original_units != translated_units:
        flags.append("unit_tokens_differ")
    if source_negation and not target_negation:
        flags.append("possible_negation_omission")
    if target_negation and not source_negation:
        flags.append("possible_negation_addition")
    if missing_terms:
        flags.append("protected_terms_missing")
    return {"source_language": source, "target_language": target, "original_numeric_tokens": original_numbers, "translated_numeric_tokens": translated_numbers, "original_unit_tokens": original_units, "translated_unit_tokens": translated_units, "source_negation_signal": source_negation, "target_negation_signal": target_negation, "missing_protected_terms": missing_terms, "flags": flags, "human_review_required": True, "translation_accuracy_established": False, "machine_translation_performed": False}

"""Script-aware, multilingual discovery triage for public research material.

Lexical cues are review prompts only. They do not determine truth, intent,
source quality, or whether a scientific claim is misleading.
"""
from __future__ import annotations

import re
import unicodedata

MAX_TEXT_CHARS = 20_000
SUPPORTED_LANGUAGES = (
    "ar", "bn", "de", "en", "es", "fr", "he", "hi", "id", "it", "ja",
    "ko", "nl", "pl", "pt", "ru", "th", "tr", "uk", "vi", "zh",
)
_CLICKBAIT = {
    "ar": ("لن تصدق", "صدمة", "سر خطير", "الحقيقة التي يخفونها"),
    "bn": ("আপনি বিশ্বাস করবেন না", "অবিশ্বাস্য", "গোপন সত্য", "চমকে যাবেন"),
    "de": ("du wirst es nicht glauben", "unglaublich", "geheime wahrheit", "was dann geschah"),
    "en": ("you won't believe", "shocking", "secret they don't want you to know", "what happened next", "doctors hate this"),
    "es": ("no podrás creer", "impactante", "la verdad oculta", "lo que pasó después"),
    "fr": ("vous n'allez pas y croire", "incroyable", "la vérité cachée", "ce qui s'est passé ensuite"),
    "he": ("לא תאמינו", "מדהים", "האמת המוסתרת", "מה שקרה אחר כך"),
    "hi": ("आप यकीन नहीं करेंगे", "चौंकाने वाला", "छिपा हुआ सच", "आगे क्या हुआ"),
    "id": ("anda tidak akan percaya", "mengejutkan", "rahasia yang disembunyikan", "apa yang terjadi selanjutnya"),
    "it": ("non ci crederai", "sconvolgente", "la verità nascosta", "cosa è successo dopo"),
    "ja": ("信じられない", "衝撃の事実", "隠された真実", "次に起きたこと"),
    "ko": ("믿을 수 없는", "충격적인 사실", "숨겨진 진실", "그 다음에 일어난 일"),
    "nl": ("je gelooft het niet", "schokkend", "verborgen waarheid", "wat er daarna gebeurde"),
    "pl": ("nie uwierzysz", "szokujące", "ukryta prawda", "co wydarzyło się później"),
    "pt": ("você não vai acreditar", "chocante", "a verdade escondida", "o que aconteceu depois"),
    "ru": ("вы не поверите", "шокирующий", "скрытая правда", "что произошло дальше"),
    "th": ("คุณจะไม่เชื่อ", "ช็อก", "ความจริงที่ถูกซ่อน", "สิ่งที่เกิดขึ้นต่อไป"),
    "tr": ("inanamayacaksınız", "şok edici", "gizlenen gerçek", "sonra ne oldu"),
    "uk": ("ви не повірите", "шокуючий", "прихована правда", "що сталося далі"),
    "vi": ("bạn sẽ không tin", "gây sốc", "sự thật bị che giấu", "điều gì xảy ra tiếp theo"),
    "zh": ("你不会相信", "震惊", "被隐藏的真相", "接下来发生了什么"),
}
_SCRIPT_RANGES = {
    "latin": ((0x0041, 0x024F), (0x1E00, 0x1EFF)),
    "cyrillic": ((0x0400, 0x052F),),
    "greek": ((0x0370, 0x03FF),),
    "arabic": ((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)),
    "hebrew": ((0x0590, 0x05FF),),
    "devanagari": ((0x0900, 0x097F),),
    "bengali": ((0x0980, 0x09FF),),
    "thai": ((0x0E00, 0x0E7F),),
    "hangul": ((0xAC00, 0xD7AF), (0x1100, 0x11FF)),
    "cjk": ((0x3040, 0x30FF), (0x31F0, 0x31FF), (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF)),
}


def _text(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("text must be a string")
    if len(value) > MAX_TEXT_CHARS:
        raise ValueError(f"text exceeds {MAX_TEXT_CHARS} characters")
    return value


def normalize_for_matching(value: str) -> str:
    """Normalize compatibility forms and diacritics without transliterating."""
    normalized = unicodedata.normalize("NFKD", unicodedata.normalize("NFKC", _text(value)).casefold())
    return " ".join("".join(
        char for char in normalized if not unicodedata.combining(char)
    ).split())


def script_profile(value: str) -> dict:
    """Count letters by broad script family; this is not language identification."""
    counts = {name: 0 for name in _SCRIPT_RANGES}
    letters = 0
    for char in _text(value):
        if not unicodedata.category(char).startswith("L"):
            continue
        letters += 1
        codepoint = ord(char)
        for name, ranges in _SCRIPT_RANGES.items():
            if any(start <= codepoint <= end for start, end in ranges):
                counts[name] += 1
                break
    return {
        "letter_count": letters,
        "script_counts": {key: count for key, count in counts.items() if count},
        "dominant_script": max(counts, key=counts.get) if any(counts.values()) else None,
        "language_identification_performed": False,
    }


def tokenize(value: str) -> list[str]:
    """Tokenize whitespace scripts and add character bigrams for CJK/Thai text."""
    normalized = normalize_for_matching(value)
    words = re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)
    extra = []
    for word in words:
        if any(
            start <= ord(char) <= end
            for char in word
            for start, end in ((0x3400, 0x9FFF), (0x0E00, 0x0E7F))
        ):
            extra.extend(word[index:index + 2] for index in range(max(0, len(word) - 1)))
    return list(dict.fromkeys(words + extra))


def _contains_phrase(text: str, phrase: str) -> bool:
    if any(
        0x3400 <= ord(char) <= 0x9FFF or 0x0E00 <= ord(char) <= 0x0E7F
        for char in phrase
    ):
        return phrase in text
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.UNICODE) is not None


def triage_title(value: str, language: str | None = None) -> dict:
    """Find configured sensationalism cues while keeping the original text intact."""
    original = _text(value)
    normalized = normalize_for_matching(original)
    if language is not None:
        if not isinstance(language, str) or language.split("-")[0].lower() not in SUPPORTED_LANGUAGES:
            raise ValueError("language must be one of the supported language codes")
        languages = [language.split("-")[0].lower()]
    else:
        languages = list(SUPPORTED_LANGUAGES)
    cues = []
    for code in languages:
        for phrase in _CLICKBAIT[code]:
            normalized_phrase = normalize_for_matching(phrase)
            if _contains_phrase(normalized, normalized_phrase):
                cues.append({"language": code, "cue": phrase})
    level = "multiple_signals" if len(cues) >= 2 else "single_signal" if cues else "no_lexical_signal"
    return {
        "original_text": original,
        "script_profile": script_profile(original),
        "matched_cues": cues,
        "matched_cue_count": len(cues),
        "triage_level": level,
        "languages_checked": languages,
        "translation_performed": False,
        "truth_or_misleadingness_determined": False,
        "scientific_evidence_status_changed": False,
        "limitations": [
            "Lexicons are deliberately conservative and incomplete.",
            "Irony, quotation, cultural context and new slang can cause false positives or misses.",
            "A missing cue is not evidence that content is reliable.",
        ],
    }

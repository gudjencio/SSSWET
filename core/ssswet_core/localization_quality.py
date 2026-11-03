def audit_translation_catalogue(source: dict[str, str], translations: dict[str, dict[str, str]], *, fallback_language: str = "en") -> dict:
    if fallback_language not in translations:
        raise ValueError("fallback language must exist")
    report = {}
    for language, catalogue in translations.items():
        missing = sorted(key for key in source if key not in catalogue or not str(catalogue[key]).strip())
        report[language] = {
            "source_count": len(source),
            "translated_count": len(source) - len(missing),
            "coverage": (len(source) - len(missing)) / len(source) if source else 1.0,
            "missing": missing,
            "fallback": language == fallback_language,
        }
    return report

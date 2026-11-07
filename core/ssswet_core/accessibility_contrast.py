"""WCAG contrast calculations for explicitly supplied rendered color pairs."""
from __future__ import annotations
import re

MAX_PAIRS = 500
_HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB = re.compile(r"^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$", re.I)

def parse_rgb(value: str) -> tuple[int, int, int]:
    if not isinstance(value, str):
        raise ValueError("colour must be a CSS hex or rgb() string")
    match = _HEX.fullmatch(value.strip())
    if match:
        digits = match.group(1)
        if len(digits) == 3:
            digits = "".join(character * 2 for character in digits)
        return tuple(int(digits[index:index + 2], 16) for index in (0, 2, 4))
    match = _RGB.fullmatch(value.strip())
    if match:
        channels = tuple(int(item) for item in match.groups())
        if all(0 <= channel <= 255 for channel in channels):
            return channels
    raise ValueError("unsupported colour; supply #RGB, #RRGGBB or opaque rgb(r,g,b)")

def _linear(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

def contrast_ratio(foreground: str, background: str) -> float:
    first, second = parse_rgb(foreground), parse_rgb(background)
    luminance_a = 0.2126 * _linear(first[0]) + 0.7152 * _linear(first[1]) + 0.0722 * _linear(first[2])
    luminance_b = 0.2126 * _linear(second[0]) + 0.7152 * _linear(second[1]) + 0.0722 * _linear(second[2])
    lighter, darker = max(luminance_a, luminance_b), min(luminance_a, luminance_b)
    return (lighter + 0.05) / (darker + 0.05)

def audit_contrast_pairs(pairs: list[dict]) -> dict:
    if not isinstance(pairs, list) or len(pairs) > MAX_PAIRS:
        raise ValueError(f"pairs must be a list of at most {MAX_PAIRS} entries")
    reports = []
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            raise ValueError("each pair must be an object")
        usage = pair.get("usage", "normal_text")
        if usage not in {"normal_text", "large_text", "ui_component"}:
            raise ValueError("usage must be normal_text, large_text or ui_component")
        try:
            ratio = contrast_ratio(pair.get("foreground"), pair.get("background"))
        except ValueError as exc:
            reports.append({"name": pair.get("name", f"pair-{index + 1}"), "valid": False, "error": str(exc)})
            continue
        aa = 3.0 if usage in {"large_text", "ui_component"} else 4.5
        aaa = 4.5 if usage == "large_text" else 7.0 if usage == "normal_text" else None
        reports.append({
            "name": pair.get("name", f"pair-{index + 1}"), "usage": usage,
            "contrast_ratio": round(ratio, 4), "wcag_aa_pass": ratio >= aa,
            "wcag_aaa_pass": ratio >= aaa if aaa is not None else None,
            "required_aa_ratio": aa, "required_aaa_ratio": aaa, "valid": True,
        })
    valid = [item for item in reports if item.get("valid")]
    return {
        "pairs_checked": len(reports), "valid_pairs": len(valid),
        "aa_pass_count": sum(item.get("wcag_aa_pass", False) for item in valid),
        "failures": [item for item in reports if not item.get("valid") or not item.get("wcag_aa_pass")],
        "results": reports, "requires_actual_rendered_colors": True,
        "gradients_images_and_transparency_not_inferred": True,
        "full_accessibility_conformance_established": False,
    }

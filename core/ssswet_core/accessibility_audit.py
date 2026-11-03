"""Small deterministic accessibility audit for public HTML fragments."""
from __future__ import annotations
import re


def audit_html(html: str) -> dict:
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    issues = []
    images = re.findall(r"<img\b[^>]*>", html, flags=re.I)
    for image in images:
        if not re.search(r"\balt\s*=\s*['\"][^'\"]*['\"]", image, flags=re.I):
            issues.append({"rule": "image-alt", "message": "Image is missing an explicit alt attribute."})
    buttons = len(re.findall(r"<button\b", html, flags=re.I))
    if buttons and not re.search(r"<main\b", html, flags=re.I):
        issues.append({"rule": "landmark-main", "message": "Interactive content should be contained in a main landmark."})
    return {"issue_count": len(issues), "issues": issues, "images_checked": len(images), "buttons_checked": buttons, "automated_audit_is_not_a_full_accessibility_review": True}

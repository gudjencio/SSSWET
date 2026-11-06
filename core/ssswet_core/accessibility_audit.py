"""Deterministic static HTML accessibility checks (not a full WCAG audit)."""
from __future__ import annotations
from collections import Counter
from html.parser import HTMLParser

MAX_HTML_CHARS = 2_000_000


class _AuditParser(HTMLParser):
    CONTROLS = {"input", "select", "textarea"}
    FOCUSABLE = {"button", "select", "textarea"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.issues = []
        self.images = self.buttons = self.main_landmarks = 0
        self.html_lang = ""
        self.ids = Counter()
        self.labels_for = set()
        self.controls = []
        self.text_targets = []
        self.headings = []
        self.label_depth = 0
        self.labelledby_refs = []

    def issue(self, rule: str, message: str, **extra):
        self.issues.append({"rule": rule, "message": message, **extra})

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        role, element_id = values.get("role", ""), values.get("id", "")
        if element_id:
            self.ids[element_id] += 1
        if tag == "html":
            self.html_lang = values.get("lang", "").strip()
        if tag == "main" or role == "main":
            self.main_landmarks += 1
        if tag == "img":
            self.images += 1
            if "alt" not in values:
                self.issue("image-alt", "Image is missing an explicit alt attribute.")
        if tag == "button":
            self.buttons += 1
        if tag in {"button", "a", "label"}:
            self.text_targets.append({"tag": tag, "text": [], "attrs": values})
        if tag == "label":
            self.label_depth += 1
            if values.get("for"):
                self.labels_for.add(values["for"])
        if tag in self.CONTROLS:
            self.controls.append({
                "tag": tag, "id": element_id, "type": values.get("type", "").casefold(),
                "value": values.get("value", ""), "aria_label": values.get("aria-label", "").strip(),
                "aria_labelledby": values.get("aria-labelledby", "").split(),
                "wrapped_label": self.label_depth > 0,
            })
        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            self.headings.append(int(tag[1]))
        if values.get("aria-labelledby"):
            self.labelledby_refs.extend(values["aria-labelledby"].split())
        if values.get("aria-hidden", "").casefold() == "true":
            focusable = tag in self.FOCUSABLE or (tag == "a" and "href" in values) or (tag == "input" and values.get("type", "text") != "hidden") or values.get("tabindex", "").strip() not in {"", "-1"}
            if focusable:
                self.issue("aria-hidden-focusable", "A focusable element is hidden from the accessibility tree.")
        if tag == "a" and not values.get("href"):
            self.issue("link-href", "An anchor element is missing an href attribute.")

    def handle_data(self, data):
        for target in self.text_targets:
            target["text"].append(data)

    def handle_endtag(self, tag):
        for index in range(len(self.text_targets) - 1, -1, -1):
            if self.text_targets[index]["tag"] == tag:
                target = self.text_targets.pop(index)
                label = " ".join(" ".join(target["text"]).split())
                attrs = target["attrs"]
                labelledby = attrs.get("aria-labelledby", "").strip()
                if tag == "button" and not (label or attrs.get("aria-label", "").strip() or attrs.get("title", "").strip() or labelledby):
                    self.issue("button-name", "Button has no detectable accessible name.")
                if tag == "a" and not (label or attrs.get("aria-label", "").strip() or attrs.get("title", "").strip() or labelledby):
                    self.issue("link-name", "Link has no detectable accessible name.")
                break
        if tag == "label":
            self.label_depth = max(0, self.label_depth - 1)


def audit_html(html: str) -> dict:
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    if len(html) > MAX_HTML_CHARS:
        raise ValueError(f"html exceeds {MAX_HTML_CHARS} characters")
    parser = _AuditParser()
    parser.feed(html)
    parser.close()
    if not parser.html_lang:
        parser.issue("document-lang", "The HTML document is missing a language declaration.")
    if parser.buttons and not parser.main_landmarks:
        parser.issue("landmark-main", "Interactive content should be contained in a main landmark.")
    for element_id, count in sorted(parser.ids.items()):
        if count > 1:
            parser.issue("duplicate-id", "An id is used more than once.", element_id=element_id, count=count)
    for control in parser.controls:
        if control["tag"] == "input" and control["type"] == "hidden":
            continue
        labelled = bool(control["aria_label"] or control["wrapped_label"] or (control["id"] and control["id"] in parser.labels_for) or control["aria_labelledby"])
        if control["type"] in {"submit", "button", "reset"} and control["value"].strip():
            labelled = True
        if not labelled:
            parser.issue("form-control-name", "Form control has no detectable accessible label.", control_id=control["id"] or None)
    known_ids = set(parser.ids)
    for reference in sorted(set(parser.labelledby_refs)):
        if reference not in known_ids:
            parser.issue("aria-labelledby-reference", "aria-labelledby references a missing id.", reference=reference)
    previous = 0
    for level in parser.headings:
        if previous and level > previous + 1:
            parser.issue("heading-order", "Heading levels skip one or more levels.", previous_level=previous, current_level=level)
        previous = level
    return {
        "issue_count": len(parser.issues), "issues": parser.issues,
        "images_checked": parser.images, "buttons_checked": parser.buttons,
        "form_controls_checked": len(parser.controls), "headings_checked": len(parser.headings),
        "automated_audit_is_not_a_full_accessibility_review": True,
        "contrast_and_keyboard_interaction_manually_verified": False,
    }

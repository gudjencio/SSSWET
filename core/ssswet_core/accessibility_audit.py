"""Deterministic static accessibility checks for public HTML fragments.

This heuristic audit catches common naming and structure failures. It is not
a substitute for keyboard, screen-reader, contrast or WCAG conformance testing.
"""
from __future__ import annotations

from html.parser import HTMLParser


class _AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.issues: list[dict] = []
        self.ids: set[str] = set()
        self.labels_for: set[str] = set()
        self.nested_label_ids: set[str] = set()
        self.inputs: list[dict] = []
        self.named_elements: list[dict] = []
        self.aria_references: list[tuple[str, str]] = []
        self.headings: list[int] = []
        self.images_checked = 0
        self.buttons_checked = 0
        self.interactive_checked = 0
        self.main_count = 0
        self.label_depth = 0

    def issue(self, rule: str, message: str, element: str = "") -> None:
        self.issues.append({"rule": rule, "message": message, "element": element})

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.casefold(): value or "" for key, value in attrs}
        element_id = attributes.get("id", "").strip()
        if element_id:
            if element_id in self.ids:
                self.issue("duplicate-id", f"Duplicate id attribute: {element_id}", tag)
            self.ids.add(element_id)
        labelledby = attributes.get("aria-labelledby", "").split()
        for reference in labelledby:
            self.aria_references.append((reference, tag))

        if tag == "main":
            self.main_count += 1
        if len(tag) == 2 and tag[0] == "h" and tag[1] in "123456":
            self.headings.append(int(tag[1]))
        if tag == "img":
            self.images_checked += 1
            if "alt" not in attributes:
                self.issue("image-alt", "Image is missing an explicit alt attribute.", tag)
            elif attributes.get("alt", "").strip():
                for active in self.named_elements:
                    active["text"] += attributes["alt"].strip() + " "

        if tag == "label":
            self.label_depth += 1
            target = attributes.get("for", "").strip()
            if target:
                self.labels_for.add(target)

        if tag == "input" or tag in {"select", "textarea"}:
            input_type = attributes.get("type", "").casefold()
            if not (tag == "input" and input_type == "hidden"):
                self.interactive_checked += 1
                self.inputs.append({
                    "tag": tag,
                    "id": element_id,
                    "type": input_type,
                    "value": attributes.get("value", ""),
                    "aria_label": attributes.get("aria-label", "").strip(),
                    "aria_labelledby": labelledby,
                    "inside_label": self.label_depth > 0,
                })
                if self.label_depth > 0 and element_id:
                    self.nested_label_ids.add(element_id)

        if tag == "button" or (tag == "a" and "href" in attributes):
            self.interactive_checked += 1
            if tag == "button":
                self.buttons_checked += 1
            self.named_elements.append({
                "tag": tag,
                "id": element_id,
                "aria_label": attributes.get("aria-label", "").strip(),
                "aria_labelledby": labelledby,
                "text": "",
            })

    def handle_data(self, data: str) -> None:
        if data.strip():
            for active in self.named_elements:
                active["text"] += data.strip() + " "

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self.label_depth:
            self.label_depth -= 1
        if tag in {"button", "a"}:
            for index in range(len(self.named_elements) - 1, -1, -1):
                if self.named_elements[index]["tag"] == tag:
                    item = self.named_elements.pop(index)
                    if not (item["aria_label"] or item["text"].strip() or item["aria_labelledby"]):
                        self.issue("interactive-name", f"{tag} has no detectable accessible name.", tag)
                    break


def audit_html(html: str) -> dict:
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    parser = _AuditParser()
    parser.feed(html)
    parser.close()

    for item in parser.inputs:
        labelledby_valid = bool(item["aria_labelledby"]) and all(
            reference in parser.ids for reference in item["aria_labelledby"]
        )
        has_label = (
            bool(item["aria_label"])
            or labelledby_valid
            or item["inside_label"]
            or (item["id"] and item["id"] in parser.labels_for)
            or (item["id"] and item["id"] in parser.nested_label_ids)
            or (item["tag"] == "input" and item["type"] in {"submit", "button", "reset"} and bool(item["value"].strip()))
        )
        if not has_label:
            parser.issue("form-control-name", "Form control has no associated label or accessible name.", item["tag"])

    for reference, tag in parser.aria_references:
        if reference not in parser.ids:
            parser.issue("aria-labelledby-reference", f"aria-labelledby references missing id: {reference}", tag)

    for previous, current in zip(parser.headings, parser.headings[1:]):
        if current > previous + 1:
            parser.issue("heading-order", f"Heading level jumps from h{previous} to h{current}.", f"h{current}")

    if parser.interactive_checked and parser.main_count == 0:
        parser.issue("landmark-main", "Interactive content should be contained in a main landmark.")
    if parser.main_count > 1:
        parser.issue("landmark-main-count", "Page contains more than one main landmark.", "main")

    return {
        "issue_count": len(parser.issues),
        "issues": parser.issues,
        "images_checked": parser.images_checked,
        "buttons_checked": parser.buttons_checked,
        "interactive_checked": parser.interactive_checked,
        "ids_checked": len(parser.ids),
        "main_landmark_count": parser.main_count,
        "automated_audit_is_not_a_full_accessibility_review": True,
    }

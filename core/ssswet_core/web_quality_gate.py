"""Static accessibility and asset-budget gate for public SSSWET web pages."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from .accessibility_audit import audit_html

DEFAULT_PAGES = ("index.html", "virtual-time-travel.html")
DEFAULT_BUDGETS = {
    "total_javascript_bytes": 3_000_000,
    "total_css_bytes": 350_000,
    "largest_javascript_bytes": 400_000,
    "largest_html_bytes": 100_000,
    "max_accessibility_issues_per_page": 0,
}


class _LocalAssetParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for key in ("src", "href"):
            value = values.get(key, "")
            if not value:
                continue
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith(("#", "data:", "mailto:")):
                continue
            path = parsed.path
            if path.lower().endswith((".js", ".css")):
                self.references.append(path)


def _within(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def audit_web_root(root: str | Path, *, pages: tuple[str, ...] = DEFAULT_PAGES, budgets: dict | None = None) -> dict:
    root = Path(root).resolve()
    limits = {**DEFAULT_BUDGETS, **(budgets or {})}
    if not root.is_dir():
        raise ValueError("web root must be an existing directory")
    page_reports, missing_assets, unsafe_assets = [], [], []
    total_issues = 0
    for relative in pages:
        page_path = root / relative
        if not _within(root, page_path) or not page_path.is_file():
            raise ValueError(f"required page is missing or unsafe: {relative}")
        html = page_path.read_text(encoding="utf-8")
        audit = audit_html(html)
        total_issues += audit["issue_count"]
        parser = _LocalAssetParser()
        parser.feed(html)
        parser.close()
        for reference in parser.references:
            target = (page_path.parent / reference).resolve()
            if not _within(root, target):
                unsafe_assets.append({"page": relative, "asset": reference})
            elif not target.is_file():
                missing_assets.append({"page": relative, "asset": reference})
        page_reports.append({
            "page": relative,
            "html_bytes": page_path.stat().st_size,
            "accessibility_issue_count": audit["issue_count"],
            "accessibility_issues": audit["issues"],
        })
    javascript = list(root.rglob("*.js"))
    stylesheets = list(root.rglob("*.css"))
    html_files = list(root.rglob("*.html"))
    js_sizes = [path.stat().st_size for path in javascript]
    css_sizes = [path.stat().st_size for path in stylesheets]
    html_sizes = [path.stat().st_size for path in html_files]
    measurements = {
        "total_javascript_bytes": sum(js_sizes),
        "total_css_bytes": sum(css_sizes),
        "largest_javascript_bytes": max(js_sizes, default=0),
        "largest_html_bytes": max(html_sizes, default=0),
        "javascript_file_count": len(javascript),
        "css_file_count": len(stylesheets),
        "html_file_count": len(html_files),
    }
    failures = []
    for key, maximum in limits.items():
        if key in measurements and measurements[key] > maximum:
            failures.append({"budget": key, "measured": measurements[key], "maximum": maximum})
    max_issues = limits["max_accessibility_issues_per_page"]
    for page in page_reports:
        if page["accessibility_issue_count"] > max_issues:
            failures.append({
                "budget": "max_accessibility_issues_per_page",
                "page": page["page"],
                "measured": page["accessibility_issue_count"],
                "maximum": max_issues,
            })
    if missing_assets:
        failures.append({"budget": "local_asset_existence", "missing": missing_assets})
    if unsafe_assets:
        failures.append({"budget": "local_asset_path_safety", "unsafe": unsafe_assets})
    return {
        "passed": not failures,
        "pages": page_reports,
        "measurements": measurements,
        "budgets": limits,
        "failures": failures,
        "missing_assets": missing_assets,
        "unsafe_assets": unsafe_assets,
        "automated_accessibility_check_is_not_a_full_wcag_audit": True,
        "contrast_and_keyboard_interaction_manually_verified": False,
    }


def assert_web_quality_gate(root: str | Path) -> dict:
    report = audit_web_root(root)
    if not report["passed"]:
        raise ValueError("public web quality gate failed: " + str(report["failures"]))
    return report

"""Regression coverage for the complete static web accessibility gate."""
from pathlib import Path

from ssswet_core.web_quality_gate import DEFAULT_PAGES, audit_web_root

ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = ROOT / "web"


def test_default_accessibility_gate_covers_every_html_page():
    html_pages = {
        path.relative_to(WEB_ROOT).as_posix()
        for path in WEB_ROOT.rglob("*.html")
    }
    assert set(DEFAULT_PAGES) == html_pages


def test_every_default_page_passes_accessibility_and_local_asset_checks():
    report = audit_web_root(WEB_ROOT)

    assert report["passed"], report["failures"]
    assert {page["page"] for page in report["pages"]} == set(DEFAULT_PAGES)
    assert all(page["accessibility_issue_count"] == 0 for page in report["pages"])
    assert report["missing_assets"] == []
    assert report["unsafe_assets"] == []

"""Validated public project-report intake for the SSSWET GitHub issue tracker."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

ALLOWED_CATEGORIES = {
    "bug", "translation", "accessibility", "performance", "security",
    "documentation", "research-quality", "reliability", "usability",
    "new-feature", "compatibility", "other",
}


def create_project_report(payload: dict) -> dict:
    """Create a non-destructive GitHub issue from a validated public report."""
    category = str(payload.get("category", "")).strip().lower()
    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()
    language = str(payload.get("language", "en")).strip().lower()[:12]
    page = str(payload.get("page", "")).strip()[:300]
    if category not in ALLOWED_CATEGORIES:
        raise ValueError("Unsupported report category")
    if not title or len(title) > 160:
        raise ValueError("A title between 1 and 160 characters is required")
    if not description or len(description) > 3000:
        raise ValueError("A description between 1 and 3000 characters is required")
    token = os.environ.get("SSSWET_GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Project report intake is not configured yet")
    repo = os.environ.get("SSSWET_REPORT_REPOSITORY", "gudjencio/SSSWET").strip()
    if repo != "gudjencio/SSSWET":
        raise RuntimeError("The configured report repository is not approved")
    body = (
        "## Public project improvement report\n\n"
        f"- **Category:** {category}\n- **Interface language:** {language}\n"
        f"- **Page:** {page or 'Not provided'}\n\n"
        "## Suggested improvement\n\n" + description +
        "\n\n---\nThis issue was submitted through the public SSSWET Report menu. "
        "It is an improvement request only. No files, features or data should be "
        "removed or changed destructively. Proposed code changes must preserve "
        "existing functionality and pass the project checks."
    )
    request = Request(
        "https://api.github.com/repos/gudjencio/SSSWET/issues",
        data=json.dumps({"title": "[Report] " + title, "body": body,
                         "labels": ["public report", "enhancement"]}).encode("utf-8"),
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {token}",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "SSSWET-public-report-intake",
                 "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=12) as response:
        result = json.loads(response.read().decode("utf-8"))
    return {"issue_number": result.get("number"),
            "issue_url": result.get("html_url"),
            "submitted": True,
            "changes_applied": False}

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ssswet_core import research_daemon
from ssswet_core.evidence_quality_matrix import EvidenceQualityMatrix

CORE = Path(__file__).resolve().parents[1]


def test_daemon_keeps_social_discovery_opt_in(monkeypatch):
    class Literature:
        def __init__(self, mailto=""):
            self.mailto = mailto

    class Combined:
        def __init__(self, literature_provider=None):
            self.literature_provider = literature_provider

    monkeypatch.setattr(research_daemon, "MultiSourceLiteratureProvider", Literature)
    monkeypatch.setattr(research_daemon, "MultiSourceResearchProvider", Combined)
    monkeypatch.delenv("SSSWET_ENABLE_SOCIAL_DISCOVERY", raising=False)
    assert isinstance(research_daemon.build_research_provider("contact@example.org"), Literature)
    monkeypatch.setenv("SSSWET_ENABLE_SOCIAL_DISCOVERY", "1")
    provider = research_daemon.build_research_provider("contact@example.org")
    assert isinstance(provider, Combined)
    assert isinstance(provider.literature_provider, Literature)


def test_cli_exposes_social_and_combined_modes_without_changing_default():
    result = subprocess.run(
        [sys.executable, "-m", "ssswet_core.research_cli", "--help"],
        cwd=CORE, capture_output=True, text=True, check=True,
    )
    assert "--provider" in result.stdout
    assert "social" in result.stdout and "combined" in result.stdout
    assert "default: demo" in result.stdout


def test_evidence_quality_matrix_surfaces_bibliographic_integrity_without_verdicts():
    dossier = {
        "dossier_id": "bibliographic-fixture",
        "sources": [
            {
                "source_id": "crossref:1", "title": "Battery study",
                "doi": "https://doi.org/10.1000/EXAMPLE", "url": "https://example.org/1",
                "source_type": "journal", "authors": ["A"], "publication_year": 2025,
                "venue": "Journal", "metadata": {"peer_reviewed": True},
            },
            {
                "source_id": "openalex:2", "title": "Other title",
                "doi": "doi:10.1000/example", "url": "https://example.org/2",
                "source_type": "journal", "authors": ["B"], "publication_year": 2025,
                "venue": "Journal", "publication_status": "retracted",
                "metadata": {"peer_reviewed": True},
            },
        ],
        "protocols": [], "runs": [], "datasets": [], "comparisons": [], "peer_reviews": [],
    }
    report = EvidenceQualityMatrix().analyze(dossier, [])
    integrity = report["bibliographic_integrity"]
    assert integrity["record_count"] == 2
    assert any(group["basis"] == "doi" for group in integrity["duplicate_groups"])
    assert integrity["retraction_signal_count"] == 1
    assert integrity["publication_status_verified"] is False
    assert report["scientific_validity_established"] is False

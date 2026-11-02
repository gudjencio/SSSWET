import pytest

from ssswet_core.evidence_dossiers import EvidenceDossierService
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.scientific_review_board import ScientificReviewBoard


def test_board_preserves_independent_opposing_assessments(tmp_path):
    store = SQLiteResearchStore(tmp_path / "board.sqlite3")
    EvidenceDossierService(store).assemble("dossier-board", "Evidence dossier", "A recorded result.")
    board = ScientificReviewBoard(store)
    common = {
        "dossier_id": "dossier-board", "conflict_status": "none_declared",
        "methods_assessment": "Methods are sufficiently described for this review.",
        "limitations": "Only the recorded dataset was assessed.",
        "evidence_refs": ["run-1", "source-1"],
    }
    board.submit(reviewer_id="reviewer-a", verdict="supports",
                 rationale="The result is consistent with the cited records.", **common)
    board.submit(reviewer_id="reviewer-b", verdict="challenges",
                 rationale="The uncertainty analysis is incomplete.", **common)
    report = board.report("dossier-board")
    assert report["count"] == 2
    assert {item["verdict"] for item in report["reviews"]} == {"supports", "challenges"}
    assert report["summaries"][0]["disagreement_recorded"] is True
    assert report["summaries"][0]["consensus_declared"] is False
    assert report["scientific_validity_established"] is False


def test_board_requires_conflict_declaration_and_substantive_fields(tmp_path):
    store = SQLiteResearchStore(tmp_path / "board.sqlite3")
    EvidenceDossierService(store).assemble("dossier-board", "Evidence dossier", "A recorded result.")
    board = ScientificReviewBoard(store)
    with pytest.raises(ValueError, match="conflict-of-interest"):
        board.submit("dossier-board", "reviewer", "supports", "", "Rationale",
                     "Methods", "Limitations", [])
    with pytest.raises(ValueError, match="rationale"):
        board.submit("dossier-board", "reviewer", "supports", "none_declared", "",
                     "Methods", "Limitations", [])


def test_board_review_events_cannot_be_updated_or_deleted(tmp_path):
    store = SQLiteResearchStore(tmp_path / "board.sqlite3")
    EvidenceDossierService(store).assemble("dossier-board", "Evidence dossier", "A recorded result.")
    board = ScientificReviewBoard(store)
    review = board.submit("dossier-board", "reviewer", "abstains", "potential",
                          "Insufficient information.", "Methods not fully described.",
                          "Substantial uncertainty remains.", [])
    with pytest.raises(Exception):
        with store._connect() as connection:
            connection.execute("DELETE FROM scientific_review_events WHERE review_id=?", (review["review_id"],))



def test_report_exposes_competing_positions_without_adjudicating(tmp_path):
    store = SQLiteResearchStore(tmp_path / "board.sqlite3")
    EvidenceDossierService(store).assemble("dossier-positions", "Evidence dossier", "A recorded result.")
    board = ScientificReviewBoard(store)
    common = {
        "dossier_id": "dossier-positions",
        "conflict_status": "none_declared",
        "methods_assessment": "The method is documented but not independently reproduced.",
        "limitations": "The available evidence is limited to one recorded dataset.",
        "evidence_refs": ["source-10"],
    }
    board.submit(
        reviewer_id="reviewer-a", verdict="supports",
        rationale="The reported pattern is consistent with the cited source.",
        **common,
    )
    board.submit(
        reviewer_id="reviewer-b", verdict="challenges",
        rationale="The uncertainty range overlaps the alternative explanation.",
        **common,
    )
    summary = board.report("dossier-positions")["summaries"][0]
    assert summary["adjudication_required_for_resolution"] is True
    positions = {item["position"]: item for item in summary["competing_positions"]}
    assert set(positions) == {"supports", "challenges"}
    assert positions["supports"]["reviewer_labels"] == ["reviewer-a"]
    assert positions["challenges"]["rationales"] == [
        "The uncertainty range overlaps the alternative explanation."
    ]
    assert positions["supports"]["evidence_refs"] == ["source-10"]
    assert summary["consensus_declared"] is False
    assert summary["scientific_validity_established"] is False

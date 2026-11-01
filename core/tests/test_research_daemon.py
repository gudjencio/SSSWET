from ssswet_core.research_daemon import TECHNOLOGY_OBJECTIVES


def test_research_daemon_covers_public_technology_catalogue():
    keys = [key for key, _ in TECHNOLOGY_OBJECTIVES]
    assert len(keys) == 32
    assert len(keys) == len(set(keys))
    assert {"artificialGravity", "medicalNanotechnology", "atmosphericRestoration"}.issubset(keys)

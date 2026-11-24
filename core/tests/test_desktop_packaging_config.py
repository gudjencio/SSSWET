import json
from pathlib import Path


def test_linux_desktop_name_matches_electron_application_id():
    repository_root = Path(__file__).resolve().parents[2]
    package = json.loads((repository_root / "package.json").read_text(encoding="utf-8"))

    assert package["desktopName"] == package["build"]["appId"]
    assert not package["desktopName"].endswith(".desktop")
    assert package["build"]["linux"]["syncDesktopName"] is True

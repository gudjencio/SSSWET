from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEDULED_WATCHES = (
    ".github/workflows/regression-watch-30m.yml",
    ".github/workflows/hourly-regression-watch.yml",
)


def test_both_scheduled_watches_execute_temporal_and_gps_regressions():
    required_commands = (
        "node --check web/temporal-clock.js",
        "node --check web/gps-scenario-model.js",
        "node web/test-temporal-clock.cjs",
        "node web/test-gps-scenario-model.cjs",
    )
    for relative_path in SCHEDULED_WATCHES:
        workflow = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        for command in required_commands:
            assert command in workflow, f"{relative_path} is missing {command!r}"

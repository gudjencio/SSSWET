from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCHEDULED_WATCHES = {
    ".github/workflows/regression-watch-30m.yml": 'cron: "*/30 * * * *"',
    ".github/workflows/hourly-regression-watch.yml": 'cron: "17 * * * *"',
}
REQUIRED_COMMANDS = (
    "node --check web/temporal-clock.js",
    "node --check web/gps-scenario-model.js",
    "node web/test-temporal-clock.cjs",
    "node web/test-gps-scenario-model.cjs",
)


def test_both_scheduled_watches_keep_their_cadence_and_temporal_gps_checks():
    for relative_path, schedule in SCHEDULED_WATCHES.items():
        workflow = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        assert schedule in workflow, f"{relative_path} changed its declared schedule"
        for command in REQUIRED_COMMANDS:
            assert command in workflow, f"{relative_path} is missing {command!r}"

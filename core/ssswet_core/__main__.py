import argparse

from .engine import SSSWETEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local SSSWET orchestration demo")
    parser.add_argument("objective", nargs="?", default="Find a harmless mathematical solution and verify it independently")
    args = parser.parse_args()

    engine = SSSWETEngine()
    task = engine.submit(args.objective, domain="mathematics")
    assignments = engine.tick()

    print(f"task={task.id}")
    print(f"assignments={assignments}")
    print(f"snapshot={engine.snapshot()}")
    print("No external AI provider is configured in this local foundation.")


if __name__ == "__main__":
    main()

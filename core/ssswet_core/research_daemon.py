"""Continuously run verification-first research passes for the public technology catalogue."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from .persistence import SQLiteResearchStore
from .pipeline import ResearchPipeline
from .providers import MultiSourceLiteratureProvider

TECHNOLOGY_OBJECTIVES = [
    ("cellular", "Cellular enhancement and safe regenerative biology"),
    ("longevity", "Healthy longevity, prevention and cellular maintenance"),
    ("armor", "Advanced protective suits, materials, ergonomics and human safety"),
    ("jetpack", "Personal propulsion, energy efficiency and controlled mobility"),
    ("translator", "Human-alien translation and uncertainty-aware communication"),
    ("spacetime", "Space-warping physics, spacetime geometry and mathematical consistency"),
    ("timetravel", "Time travel, causality, relativity and theoretical temporal models"),
    ("cleanenergy", "Clean energy systems and scalable low-carbon generation"),
    ("energyStorage", "Advanced energy storage, safer batteries and long-duration storage"),
    ("water", "Clean water purification and low-energy desalination"),
    ("foodSystems", "Sustainable food systems, resilient crops and food preservation"),
    ("climate", "Climate adaptation, heat resilience and flood preparedness"),
    ("biodiversity", "Biodiversity protection, habitat connectivity and conservation measurement"),
    ("wildlife", "Wildlife protection, ethical tracking and rescue support"),
    ("oceans", "Ocean observation, marine pollution reduction and ecosystem restoration"),
    ("reforestation", "Reforestation, habitat restoration and ecological corridors"),
    ("agriculture", "Regenerative agriculture, soil health and biodiversity-friendly farming"),
    ("circularEconomy", "Circular economy, repairability and safer material recovery"),
    ("airQuality", "Clean air sensing, filtration and emissions monitoring"),
    ("mobility", "Sustainable mobility, safer cycling and efficient low-emission logistics"),
    ("accessibility", "Assistive and accessibility technology for inclusive independent living"),
    ("disasterResilience", "Disaster prevention, early warning and resilient response systems"),
    ("publicHealth", "Public health prevention, accessible diagnostics and community resilience"),
    ("sanitation", "Safe sanitation, wastewater treatment and water reuse"),
    ("education", "Open science, scientific literacy and accessible research education"),
    ("animalHealth", "Animal health, welfare, non-invasive diagnostics and veterinary access"),
    ("materials", "Sustainable, recyclable and safer non-toxic materials"),
    ("carbonMonitoring", "Carbon and ecosystem monitoring with transparent measurement"),
    ("pollinators", "Pollinator protection, habitat mapping and exposure reduction"),
    ("artificialGravity", "Artificial gravity, inertial management and safe theoretical models"),
    ("medicalNanotechnology", "Medical nanotechnology for diagnostics, monitoring and future therapies"),
    ("atmosphericRestoration", "Atmospheric restoration, pollution reduction and resilient air-quality systems"),
]


def run_pass(database: str, mailto: str = "") -> None:
    store = SQLiteResearchStore(database)
    provider = MultiSourceLiteratureProvider(mailto=mailto)
    pipeline = ResearchPipeline(provider=provider, store=store)
    for technology, objective in TECHNOLOGY_OBJECTIVES:
        try:
            task_id, steps = pipeline.start(objective, domain=technology)
            print(f"[SSSWET] {technology}: {task_id} · {len(steps)} research-agent passes")
        except Exception as exc:
            print(f"[SSSWET] {technology}: research pass blocked ({type(exc).__name__}: {exc})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run continuous SSSWET technology research locally")
    parser.add_argument("--database", default=".ssswet/ssswet.sqlite3")
    parser.add_argument("--interval-hours", type=float, default=1.0)
    parser.add_argument("--mailto", default="")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.interval_hours <= 0:
        parser.error("--interval-hours must be greater than zero")
    database = str(Path(args.database))
    while True:
        run_pass(database, args.mailto)
        if args.once:
            return
        time.sleep(args.interval_hours * 3600)


if __name__ == "__main__":
    main()

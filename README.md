# SSSWET

**Super Soldier Space Warping Engeriening Tech**  
**ETDESS — traduction française de SSSWET**

SSSWET is the project's official name. ETDESS is its French translation.

## Mission

SSSWET is an experimental research platform intended to organize computational research, simulations, verification, scientific literature review, and collaborative AI-agent workflows toward humanitarian technologies.

The project is designed to move from **idea → decomposition → research → testing → verification → reproducible evidence → real-world validation**, without pretending that an ambitious objective is already solved.

## Current architecture

The first executable research pipeline is now being assembled from independent layers:

- **Task Orchestrator** — queues objectives, schedules agents, preserves blocked work, and changes strategy.
- **Task Decomposer** — converts a broad objective into smaller, independently checkable work units.
- **Specialist Groups** — allows several research roles to collaborate on one task without requiring every agent to perform every job.
- **Knowledge Exchange** — stores statements together with their evidence, confidence, and verification state.
- **Strategy Selector** — rotates approaches when an attempt is blocked or inconclusive.
- **Verification Engine** — performs independent checks and keeps uncertainty explicit.
- **Safety Gate** — prevents insufficiently verified or high-risk conclusions from being treated as ready for real-world use.
- **Provider Interface** — separates the orchestration system from future AI, computation, and research providers.
- **Deterministic Demo Provider** — provides a local, credential-free implementation for development and testing.
- **Simulation layer** — keeps simulated evidence distinct from physical evidence.

The provider boundary is intentional: real model/search providers can be connected later through adapters and environment-based credentials without placing secrets in the public repository.

## Core principles

- No weapons development.
- No intentional design of systems whose known purpose is to injure or kill people.
- Agent agreement is never treated as proof.
- Results are independently checked, reproduced where possible, and labelled with uncertainty and limitations.
- High-risk medical, biological, aerospace, or physical applications require qualified human and regulatory review before real-world use.
- Dangerous or unverified approaches are not published as actionable instructions.
- Failed approaches are recorded at an appropriate level so the system can change strategy rather than silently repeating the same failure.
- Research agents can be created, paused, replaced, or retired according to workload and verification needs.
- Runtime self-modification of executable safety/orchestration code is not permitted; improvements are versioned, reviewed, tested, and released deliberately.

## Planned platform

- Dynamic multi-agent research orchestrator
- Task decomposition and specialist-agent groups
- Independent verification and adversarial review
- Mathematical and scientific computation
- Simulation and reproducibility tests
- Shared validated knowledge
- Research/source reliability scoring
- Stuck-agent strategy changes and recovery
- Safe checkpoints and state restoration
- Public research summaries and changelog
- Web interface
- Downloadable desktop software
- Mobile application
- Versioned GitHub releases for major/global updates
- Large multilingual interface

## Research areas

Mathematics, physics, engineering, materials science, robotics, computing, aerospace, space science, Earth sciences, biology and medicine can be represented as research domains. Extraordinary objectives are treated as hypotheses and research questions, never as guaranteed capabilities.

## Scientific honesty

SSSWET does **not** claim that software can guarantee zero errors or establish absolute physical safety merely through computation or AI consensus. Its goal is to push verification as far as practical: independent calculations, contradictory checks, simulations, reproducibility, source comparison, explicit uncertainty, and human validation where required.

## Public project links

- X: https://x.com/ssswetech
- Instagram: https://www.instagram.com/ssswetech
- YouTube: https://www.youtube.com/@ssswetech
- Contact: ssswetindustries@gmail.com

## Run the local interface

The repository includes a local, read-only interface backed by the Python core. It serves the web application and exposes local status, event summaries, and validated knowledge. It does not accept arbitrary public task submissions.

```bash
cd core
python -m pip install -e .
ssswet-local
```

Then open `http://127.0.0.1:8765`. The default server binds only to the local computer. GitHub Pages remains a static preview and does not run the Python research engine.

## Project status

**Early architecture / active implementation.**

The repository is being built incrementally. Desktop and mobile packaging will use versioned releases so users can download a new build when substantial improvements are made.

## Author

Gudjencio Hermann MARTIN

## Persistent research history

Local research runs can now be saved in SQLite and reopened through the
read-only local interface. The CLI and interface can share the same database:

```bash
cd core
python -m pip install -e .
ssswet-run --objective "Study wave propagation" --domain physics --corpus documents.json
ssswet-local
```

Both commands use `.ssswet/ssswet.sqlite3` by default. Research outputs are
stored as unverified until the separate evidence and reproduction requirements
are met. See [core documentation](core/README.md) for details.

### External literature discovery

The local research runner can now query Crossref for bibliographic metadata:

```bash
ssswet-run --objective "wave propagation measurement methods" --domain physics --provider crossref
```

The returned publications are source leads, not verified conclusions. All
provider outputs remain explicitly unverified pending full source review,
independent evidence and reproducibility.

Shared knowledge entries and their validation states are also retained in the
local SQLite database and reloaded when the engine restarts. Unverified
candidates remain separate from verified knowledge.

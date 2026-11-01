# SSSWET Core — Developer Guide

This package provides the local research engine, command-line tools, persistence layer and read-only API used by the SSSWET application. The guide documents the current interfaces and their verification boundaries for developers and research operators.

## Agent lifecycle

1. Define a precise task.
2. Assign the smallest useful number of specialist agents.
3. Let agents research or calculate independently.
4. Exchange relevant findings.
5. Run independent verification.
6. Run simulations/tests where applicable.
7. Classify the result and its uncertainty.
8. Publish only sufficiently supported conclusions.
9. Checkpoint the safe state.
10. Reassign, pause, replace, or retire agents according to workload.

## Recovery

A blocked agent must preserve the problem statement, then retry using a materially different strategy. Repeated loops are detected and interrupted. New agents can inherit the relevant validated knowledge without inheriting an unverified conclusion as fact.

## Scaling

The orchestrator should create additional agents when workload requires it, split work into groups when several tasks can run concurrently, and reduce idle agents when resource pressure becomes significant.

## Verification states

- `hypothesis`
- `candidate`
- `simulated`
- `independently_verified`
- `reproduced`
- `requires_real_world_validation`
- `rejected`

An agent consensus is not, by itself, scientific proof.

## Evidence independence and disagreement review

Evidence is retained with its source identity. Two evidence entries from the
same source do not count as independent verification. A finding can only enter
the independently verified state after at least two distinct source IDs have
been recorded. Reproduction also requires a separate reproduction-run ID.

Structured claims can be compared by subject, predicate and asserted value.
When distinct sources assert incompatible values, the engine records a
`disagreement_detected` event and queues one independent review task for that
conflict signature. The review is not automatically considered resolved:
the reviewer must inspect source quality, methods, context and uncertainty.
Free-form text is not silently interpreted as structured scientific claims.

Repeated detection of the same conflict does not create an unlimited queue of
duplicate review tasks. Unresolved claims remain unresolved until reviewed.

## Source quality rubric

Source assessments record visible factors: peer review, primary-source status,
availability of methods, known publication date, HTTPS URL and declared
limitations. The resulting score is a prioritization aid, not a probability
of truth and not a substitute for claim-level verification. A high source
score never automatically upgrades a finding's verification state.

## Role-based team execution

The pipeline allocates one agent per decomposed role, creates a research group,
records each pass as a structured event, and releases the team when the run
finishes. If a provider fails, the parent task is preserved in the queue and
the allocated agents are released. The agent pool grows only to meet unmet
workload and remains bounded by its configured maximum.

## Local document research

`LocalCorpusProvider` searches a caller-supplied corpus using transparent
lexical overlap. It returns the matching document IDs and excerpts, but does
not claim semantic understanding or scientific verification.

Install the core and run:

```bash
cd core
python -m pip install -e .
ssswet-run --objective "Compare published methods for measuring wave propagation" --domain physics --corpus documents.json
```

The corpus is a JSON array. Each entry has `source_id`, `title`, `text`,
and an optional `url`. The command labels all provider output as unverified.
Without `--corpus`, it uses the deterministic demo provider.

## Persistent local research history

SSSWET can store research runs in a local SQLite database using only the
Python standard library. Tasks, lifecycle events, source identifiers, provider
summaries and evidence excerpts are retained across restarts. Stored provider
outputs are explicitly classified as `unverified`; persistence does not
upgrade scientific confidence.

The command-line runner writes to `.ssswet/ssswet.sqlite3` by default:

```bash
ssswet-run --objective "Study wave propagation" --domain physics --corpus documents.json
```

Choose another database with `--database /path/to/history.sqlite3`.

Run the local read-only interface against the same database:

```bash
ssswet-local --database .ssswet/ssswet.sqlite3
```

The API exposes recent tasks at `/api/work`, provider outputs at
`/api/discoveries`, event history at `/api/events`, and independently
validated memory at `/api/verified`. The interface never treats a stored
provider output as a verified discovery.

## External scholarly discovery with Crossref, OpenAlex and arXiv

Public Crossref and OpenAlex metadata providers retrieve bibliographic records for multidisciplinary literature searches. An additional arXiv provider retrieves preprint metadata and abstracts, which can be useful in physics, mathematics, computing and related fields. Crossref records DOI/URL, title, author metadata, publisher and publication year. OpenAlex adds work identifiers, venue metadata and citation counts when available. Neither provider fetches paywalled full text, interprets a paper, or validates scientific claims. The combined provider deduplicates DOI matches and labels the catalogue supplying each record.

Example:

```bash
ssswet-run --objective "wave propagation measurement methods" --domain physics --provider literature
```

Use `--provider crossref`, `--provider openalex` or `--provider arxiv` to query a single catalogue. An optional contact email can be supplied with `--mailto` for Crossref and OpenAlex. arXiv records may be preprints and are not necessarily peer reviewed.

Crossref and OpenAlex results are discovery leads only and remain marked unverified. Network failures or
empty results are reported without fabricating substitute evidence.

### Shared knowledge across restarts

The SQLite store also retains shared knowledge entries and their original
validation flags. The engine reloads these entries when constructed with the
same store. Unvalidated candidates remain unvalidated; only an explicit
validated record appears in the verified-memory endpoint. Use
`engine.remember_knowledge(MemoryItem(...))` to write a record through the
persistent engine facade.

## Optional language-model research provider

SSSWET now includes an adapter for APIs that implement the OpenAI-compatible
chat-completions format. It can connect to a hosted provider or a compatible
local model server. No API key is stored in the repository or SQLite history.

Set credentials in the local shell (never commit them):

```bash
# Linux / macOS
export SSSWET_LLM_API_KEY="your-secret-key"
export SSSWET_LLM_MODEL="your-model-id"
# Optional: override the API endpoint
export SSSWET_LLM_ENDPOINT="https://api.openai.com/v1/chat/completions"
```

Then run:

```bash
ssswet-run --objective "Compare published methods for measuring wave propagation" --domain physics --provider llm
```

The default endpoint is an OpenAI-compatible chat-completions URL; a different
compatible endpoint can be selected with `--endpoint`. Non-local endpoints
must use HTTPS. Plain HTTP is accepted only for localhost model servers.

Model responses are labelled as generated drafts. They are not evidence,
citations, measurements, or verified discoveries. The provider deliberately
does not promote model-written references into source records. Human review,
real source retrieval, independent checks and reproducibility remain required.


## Local PDF document extraction

Install the optional PDF dependency:

```bash
python -m pip install -e ".[pdf]"
```

Pass one or more PDFs to the local runner; they are extracted page by page and
combined with an optional JSON corpus:

```bash
ssswet-run --objective "Compare experimental methods and limitations" --domain physics --pdf ./paper-a.pdf --pdf ./paper-b.pdf
ssswet-run --objective "Review this topic" --corpus documents.json --pdf ./paper-a.pdf
```

Each non-empty page becomes a separate local corpus document with a page-level
identifier. Extraction is bounded to 50 MiB per file, 500 pages per file and
12,000 characters per page. Encrypted PDFs are rejected.

When `--provider llm` is combined with local PDFs or a JSON corpus, SSSWET
retrieves up to 12 relevant page-level passages and asks the configured model
for a structured review: hypotheses, methods, reported results, explicitly
present equations/parameters, limitations, cross-source agreements and
contradictions, missing information, and safe verification steps. The model
must identify source IDs for its statements. This remains a model-generated
analysis, not independent scientific verification; lexical retrieval can miss
relevant passages, and the selected excerpts are sent to the configured model
provider. Image-only scanned
pages require OCR, which is not yet included. Files are read locally and are
not uploaded by this feature. Extracted text can contain parsing errors and
must be checked against the original PDF; it is not automatically evidence
or a verified conclusion.


### Conservative verification states

The verification engine does not infer independence from different citation IDs.
A reviewer must provide a provenance group (for example, the originating research
team or dataset lineage) and explicitly confirm that the source has been assessed
as independent. Two records from the same provenance group count as one group.
A reproduction state also requires explicit confirmation that a separate
reproduction run was completed; supplying a run label alone is insufficient.
These flags record an assessment, not an automatic audit of the underlying
research. High-risk findings still require qualified real-world validation.


### Scientific source provenance registry

The local SQLite store can register bibliographic provenance using
`SQLiteResearchStore.register_source(SourceRecord(...))`. Records can retain
DOIs, authors, institutions, dataset identifiers, declared related publications,
and an explicitly supplied provenance group. Use `get_source`,
`find_sources_by_doi`, `sources_sharing_provenance`, and
`source_dependency_report` to inspect the registry.

Dependency reports flag declared relationships, shared dataset identifiers,
matching DOIs, and matching provenance groups. These are review signals only:
shared datasets may be legitimate, metadata may be incomplete, and the registry
does not infer scientific independence automatically. A human reviewer must
assess provenance before recording an independent source group. The registry
does not crawl publisher sites or verify authorship/institution claims by itself.


### Persistent knowledge graph

The local SQLite database can now store explicit knowledge nodes and typed
relationships. Node types include hypotheses, findings, sources, datasets,
experiments, questions, methods and concepts. Relationships include
`supports`, `contradicts`, `derived_from`, `tests`, `uses_dataset`,
`related_to`, `answers` and `requires_verification`.

Create nodes with `KnowledgeNode` and connect existing nodes with
`KnowledgeEdge`; both are available from `ssswet_core.knowledge_graph`.
The store exposes `add_knowledge_node`, `add_knowledge_edge`,
`knowledge_graph` and `knowledge_neighbors`. Edge endpoints must already
exist. Repeated node IDs and edge triples are updated idempotently.

The read-only local API exposes a bounded graph snapshot at
`/api/knowledge-graph`. This endpoint returns stored metadata and explicit
relationships; it does not infer missing links, establish causality, or upgrade
verification states. A relationship such as `supports` records an attributed
claim about evidence, not proof that the connected finding is true.


### Research-gap analysis

The deterministic `ResearchGapAnalyzer` inspects the explicit knowledge graph
and reports missing recorded support, untested hypotheses, pending verification,
unresolved support/contradiction links, unanswered questions, unlinked experiments
and findings without provenance links. It prioritizes review work (high/medium/low)
and proposes a next action for each gap.

Run it locally with:

```python
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.research_gaps import ResearchGapAnalyzer

store = SQLiteResearchStore()
report = ResearchGapAnalyzer().report(store.knowledge_graph())
print(report)
```

The read-only local API also exposes this report at `/api/research-gaps`.
The analyzer is deliberately conservative: missing graph relationships are
not proof that evidence or experiments do not exist elsewhere. It never creates
evidence, changes verification states, or declares a hypothesis true or false.


### Experimental planning and records

`ssswet_core.experimentation` provides structured experiment plans,
separate simulation/real-observation records, and explicit comparison against
a supplied prediction. `draft_experiment_plan` creates a deliberately
incomplete scaffold from a hypothesis: it does not invent variables, methods,
controls, measurements or safety procedures. `validate_experiment_plan`
lists missing design information before review.

Example:

```python
from ssswet_core.experimentation import draft_experiment_plan
from ssswet_core.persistence import SQLiteResearchStore

store = SQLiteResearchStore()
plan = draft_experiment_plan(
    "experiment-001",
    "hypothesis-001",
    "The measured response changes with the input parameter",
)
store.save_experiment_plan(plan)
print(store.get_experiment_plan("experiment-001"))
```

Save a record with `make_experiment_record(..., kind="simulation" | "real_observation", ...)`
and `store.save_experiment_record(record)`. Records are persisted separately
from the plan, and simulation records cannot be mistaken for real observations.
The read-only API endpoint `/api/experiments` returns up to 100 saved plans and
their records.

A comparison such as `consistent_with_prediction` only means the explicitly
provided value matches the explicitly supplied prediction under the chosen
comparison rule. It does not prove a hypothesis. Assessments require human
review; real-world execution requires domain-specific safety, ethical,
regulatory and professional approval. SSSWET does not automatically execute
physical experiments or promote simulated output to verified evidence.


### Multi-model comparison

`ssswet_core.model_comparison.MultiModelComparator` runs two or more
explicitly configured model callables against the same prompt and records each
output separately. It reports identical text, divergent text, or insufficient
outputs when a model fails. Each output has a SHA-256 digest for traceability.

The comparator does not use majority voting, rank model quality, or treat
agreement as independent evidence. Different model IDs and provider labels do
not establish statistical independence. Model outputs remain drafts and
must be checked against traceable sources and appropriate expert review.

Example:

```python
from ssswet_core.model_comparison import MultiModelComparator

comparison = MultiModelComparator().compare(
    "comparison-001",
    "Identify testable explanations for the observed phenomenon",
    {
        "model-a": ("provider-a", lambda prompt: "First model response"),
        "model-b": ("provider-b", lambda prompt: "Second model response"),
    },
)
print(MultiModelComparator.to_dict(comparison))
```


### Reproducible multi-model simulation studies

`ssswet_core.simulation_study.MultiModelSimulationRunner` runs at
least two explicitly configured computational models against the same set of
caller-supplied scenarios. Each scenario's parameter values are serialized in
a stable order, and every model output is retained with a SHA-256 digest,
provider/model labels and an individual success/failure status. Scenario
comparisons are classified as identical, divergent or insufficient.

The runner is deliberately bounded to 100 scenarios and 20 models per study.
It does not generate physical experiments, invent scientific equations, search
unbounded parameter spaces, or decide which model is correct. It calls only
the Python functions supplied by the local operator.

Example:

```python
from ssswet_core.simulation_study import (
    MultiModelSimulationRunner,
    SimulationScenario,
)

study = MultiModelSimulationRunner().run(
    "study-001",
    "Compare two illustrative mathematical models",
    [
        SimulationScenario("baseline", {"input": 2}),
        SimulationScenario("variant", {"input": 5}),
    ],
    {
        "model-a": ("local", lambda p: {"output": p["input"] ** 2}),
        "model-b": ("local", lambda p: {"output": p["input"] * 3}),
    },
)
print(MultiModelSimulationRunner.to_dict(study))
```

A completed simulation is not a real observation. Identical outputs do not
establish model validity or independence. Divergent outputs are preserved for
investigation rather than resolved by majority vote. Model assumptions,
equations, units, calibration and domain of validity require expert review.


### Adaptive simulation scenario optimization

`ssswet_core.adaptive_optimization.AdaptiveScenarioOptimizer` ranks a finite
set of explicitly supplied candidate scenarios using prior numeric scores.
It combines two transparent heuristics with equal weight: a nearest-neighbour
score estimate (exploitation) and normalized distance from previously scored
scenarios (exploration). The operator chooses whether lower or higher scores
are preferred.

The candidate list must include the scenarios referenced by observations, so
the optimizer can recover their parameter vectors. Already observed candidates
are excluded from new proposals. The optimizer does not execute simulations,
invent parameter ranges, fit a scientific model, or claim global optimality.
It is bounded to 10,000 candidates and 10,000 observations.

Example:

```python
from ssswet_core.simulation_study import SimulationScenario
from ssswet_core.adaptive_optimization import (
    AdaptiveScenarioOptimizer,
    ScenarioObservation,
)

report = AdaptiveScenarioOptimizer().propose(
    [
        SimulationScenario("baseline", {"input": 1}),
        SimulationScenario("candidate-a", {"input": 3}),
        SimulationScenario("candidate-b", {"input": 8}),
    ],
    [ScenarioObservation("baseline", 2.5)],
    count=2,
    direction="maximize",
)
print(AdaptiveScenarioOptimizer.to_dict(report))
```

The nearest-neighbour estimate simply carries forward the score of the closest
observed scenario. The exploration and combined selection scores are ranking
heuristics, not probabilities, confidence intervals, causal explanations or
proof of an optimum. Their usefulness depends on the supplied candidate range,
parameter units/scaling and quality of the objective scores. Review proposals
before running expensive or safety-relevant simulations.


### Connected adaptive research cycle

`ssswet_core.adaptive_cycle.propose_from_study` connects a completed
multi-model simulation study to the adaptive optimizer. It accepts objective
scores explicitly reviewed and supplied by the operator; it never guesses a
score from raw model output. A scored scenario must have at least two
successfully completed model runs in the study. The optimizer then ranks
unobserved candidates from the caller-supplied finite set.

The returned cycle is explicitly marked `proposal_only`. The local SQLite
store can persist each cycle with `save_adaptive_cycle`, retrieve it with
`get_adaptive_cycle`, and list history with `adaptive_cycle_history`.
The read-only local API exposes recent history at `/api/optimization`.

Example:

```python
from ssswet_core.adaptive_cycle import propose_from_study
from ssswet_core.persistence import SQLiteResearchStore
from ssswet_core.simulation_study import SimulationScenario

cycle = propose_from_study(
    completed_study,
    [
        SimulationScenario("baseline", {"input": 1}),
        SimulationScenario("candidate-a", {"input": 3}),
    ],
    reviewed_scores={"baseline": 2.5},  # explicitly assessed by an operator
    count=1,
    direction="maximize",
)
store = SQLiteResearchStore()
store.save_adaptive_cycle("cycle-001", cycle)
```

No proposed scenario is executed automatically. Human approval is required
before a proposal is turned into another simulation run. The scores supplied
to this bridge are operator assessments, not automatically inferred scientific
measurements. Simulation output remains separate from real-world observation
and verified findings.


### Research campaign manager

The campaign manager groups related work into explicit milestones without
claiming that workflow completion equals scientific success. A campaign has
a controlled lifecycle (`draft`, `active`, `paused`, `blocked`,
`completed`). Completion is rejected until every milestone is marked
completed. Milestones can link to study IDs and retain operator notes.

```python
from ssswet_core.campaigns import CampaignMilestone, create_campaign, set_campaign_state
from ssswet_core.persistence import SQLiteResearchStore

campaign = create_campaign(
    "campaign-001",
    "Wave propagation methods",
    "Compare measurement approaches",
    "physics",
    [CampaignMilestone("review", "Literature review", "Map published methods")],
)
campaign = set_campaign_state(campaign, "active")
SQLiteResearchStore().save_campaign(campaign)
```

Campaigns persist in SQLite and the local read-only API exposes their
summaries at `/api/campaigns`. This first version tracks milestones and
links; it does not yet schedule agents, allocate compute budgets, or launch
experiments. Those capabilities will be added behind explicit operator
approval and resource limits.


### Campaign resource manager

`ssswet_core.resource_manager.ResourceManager` provides bounded scheduling
for campaign work. It tracks queued and active tasks, specialist roles,
priority, campaign-level parallelism, estimated/reserved/consumed resource
units, duplicate-work keys and per-task attempt history.

A failed assignment releases its agent and is requeued up to the configured
attempt limit. Exhausted failures remain visible and cannot be silently
resubmitted under the same task ID. Actual resource usage is checked against
the campaign quota before the assignment is closed. The manager exposes a
serializable `snapshot()`; snapshots can be persisted with
`SQLiteResearchStore.save_resource_snapshot` and read from the local
read-only `/api/resources` endpoint.

```python
from ssswet_core.resource_manager import ResourceManager, WorkRequest
from ssswet_core.persistence import SQLiteResearchStore

manager = ResourceManager(max_active_assignments=8, max_attempts=3)
manager.configure_campaign("campaign-001", max_parallel=2, max_units=50)
manager.submit(WorkRequest(
    task_id="task-001",
    campaign_id="campaign-001",
    objective="Compare published measurement methods",
    role="literature_analyst",
    estimated_units=2,
    priority=2,
    deduplication_key="campaign-001:literature-review",
))
assignments = manager.dispatch()
# The caller runs only approved, bounded work and reports its outcome:
if assignments:
    manager.finish(assignments[0].request.task_id, success=True, actual_units=1.5)
SQLiteResearchStore().save_resource_snapshot("snapshot-001", manager.snapshot())
```

This is a deterministic local scheduler, not a self-running cloud cluster.
Resource units are operator-defined accounting units, not a claim about CPU,
GPU, energy or monetary cost. Snapshot persistence is explicit; it does not
yet restore live agent processes or automatically resume interrupted work.


### Campaign milestone coordination

`ssswet_core.coordinator.CampaignCoordinator` connects saved campaign
milestones to the bounded resource scheduler. It checks campaign and milestone
states before queueing work, assigns specialist roles within configured
campaign quotas, records attempts and resource snapshots, and preserves queued
work when a campaign is paused.

A successful scheduler assignment is not equivalent to scientific completion.
The coordinator leaves a milestone in progress after work finishes; an
authorized operator must explicitly approve milestone completion. Exhausted
failed attempts mark the milestone as blocked for review. Dispatch only
allocates local agents and reserves operator-defined resource units; it does
not invoke providers, run experiments or perform physical actions.

```python
from ssswet_core.coordinator import CampaignCoordinator
from ssswet_core.persistence import SQLiteResearchStore

store = SQLiteResearchStore()
coordinator = CampaignCoordinator(store)
coordinator.configure_campaign(
    "campaign-001",
    max_parallel=2,
    max_units=20,
)
coordinator.enqueue_milestone(
    "campaign-001",
    "literature-review",
    "literature_analyst",
    estimated_units=2,
    priority=2,
)
assignments = coordinator.dispatch()
# The operator or an approved worker reports the completed assignment:
if assignments:
    task_id = assignments[0].request.task_id
    coordinator.finish_assignment(task_id, success=True, actual_units=1.5)
    # Completion is a separate, explicit review decision:
    coordinator.approve_milestone_completion(
        "campaign-001", "literature-review"
    )
```

The coordinator uses the campaign and resource records already stored in
SQLite. Its snapshots are available through the existing read-only
`/api/resources` endpoint. A paused or completed campaign cannot dispatch new
milestone work.


### Cross-campaign knowledge collaboration

The `ssswet_core.collaboration` module introduces explicit, auditable
knowledge-transfer requests between two existing research campaigns. A
request must reference an existing knowledge-graph node and both campaigns.
The receiving campaign can accept or reject the request with a decision note.
Only pending transfers can be decided, and the transfer history is retained.

Accepting a transfer records the hand-off; it does not copy a claim into
verified knowledge or alter the original node's verification state. The
local read-only API exposes `/api/collaboration/transfers` and
`/api/collaboration/campaign/{campaign_id}/conflicts`.

The conflict report surfaces explicitly recorded `contradicts` graph edges
whose endpoint metadata names the requested campaign. It is a review queue,
not an automatic scientific verdict. A human reviewer must inspect the
underlying evidence and provenance before resolving a disagreement.

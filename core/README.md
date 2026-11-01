# SSSWET Core

The core will coordinate research agents without exposing the agent-generation mechanism to the agents themselves.

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

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

## External scholarly discovery with Crossref and OpenAlex

Public Crossref and OpenAlex metadata providers retrieve bibliographic records for multidisciplinary literature searches. Crossref records DOI/URL, title, author metadata, publisher and publication year. OpenAlex adds work identifiers, venue metadata and citation counts when available. Neither provider fetches paywalled full text, interprets a paper, or validates scientific claims. The combined provider deduplicates DOI matches and labels the catalogue supplying each record.

Example:

```bash
ssswet-run --objective "wave propagation measurement methods" --domain physics --provider literature
```

Use `--provider crossref` or `--provider openalex` to query a single catalogue. An optional contact email can be supplied with `--mailto`.

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

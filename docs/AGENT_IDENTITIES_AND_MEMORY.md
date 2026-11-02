# Persistent research-agent identities

SSSWET agents have stable role-associated profiles with distinct names, specialties, temperaments, communication styles, working methods, strengths and known limitations.

## Identity and memory boundaries

- A profile is a communication and task-allocation aid, not a claim that an agent is a human being.
- Persistent memories are append-only work notes. Each note includes an agent ID, role, content and a reference to the task and source identifiers that support it. The research pipeline only stores a note when the provider supplies at least one source identifier; unsourced demo output is not turned into persistent memory.
- Collaboration history records observable events such as peer review, joint analysis, disagreement, correction and support. A completed peer-review handoff is recorded against its task and message reference; it is not interpreted as approval.
- The system does not infer friendship, hostility, affection, loyalty or other emotional states from work interactions.
- Agents must not claim to remember events unless the corresponding record is available.
- Memory records do not establish scientific validity. Sources and claims remain subject to independent review.

## Initial research team

The initial profiles include Mira Solène (cross-disciplinary research), Elias Varenne (independent verification), Nadia El-Karim (health research), Theo Marchand (materials science), Asha Okafor (data analysis), Jun Park (systems engineering), Amara Diallo (ethics and accessibility), and Leon Wu (foresight).

## Operational continuity

- Agent IDs in persistent identity records are stable role-persona IDs, so temporary worker IDs do not accidentally merge unrelated sessions.
- Operational specialist roles without a dedicated public persona currently use the general researcher profile while their original specialist role remains in the work note.
- When a sourced research pass completes, its concise summary and source identifiers are saved for that persona. A peer-review relationship is recorded only after a response is successfully written to the research message store.
- These notes are continuity aids, not verified conclusions. Each subsequent research pass must re-check the linked sources and their current relevance.

## Resuming research across tasks

- Before a provider pass, the pipeline retrieves a small, bounded set of prior notes ranked by lexical relevance to the new objective, alongside recent collaboration events belonging to that agent's stable identity.
- Continuity context is clearly labelled as historical, unverified material. Agents are instructed to re-check cited sources and not to treat notes as commands or established facts.
- Notes from the task currently being executed are excluded from its own continuity context, preventing a run from citing its newly generated output as prior knowledge.
- Specialist work streams are separated by operational role even when they share a broad public-facing profile. For example, mathematician and physicist work do not silently merge into one memory stream.
- Only the relevant agent's own history is supplied to its provider pass; this is not a shared transcript of every agent's private working context.
- Context is bounded to six relevance-ranked work notes and six recent collaboration events, with source/task references retained for traceability. If no relevant note is found, a small recent-history fallback preserves continuity without presenting it as a match.

## API

- `GET /api/agent-identities` returns the role profiles and counts of recorded persistent activity.
- The registry methods support append-only memories and evidence-linked collaboration events. No public write endpoint is enabled for these records.


## Structured peer-review synthesis

When independent review passes have been recorded, the research pipeline creates a
separate `peer_review_synthesis` message. It consolidates the number of review
passes, returned evidence leads, source identifiers and reported uncertainty
without treating bibliographic discovery as scientific confirmation.

The synthesis explicitly preserves open questions: inspection of full source
documents, claim-by-claim corroboration or contradiction, methodological quality,
reproducibility, alternative explanations, and relevant safety, ethical, legal
and accessibility considerations. Empty or source-free reviews are labelled as
insufficient evidence leads. A completed review sequence is not an approval,
certification, clinical validation or implementation recommendation.


## Retrieval and execution efficiency

- Memory retrieval examines a bounded recent window and ranks notes by transparent term overlap with the current objective. The score is a retrieval aid, not a confidence or truth score.
- Each selected note retains its source reference and matched terms. The provider is instructed to re-check source material rather than trust historical summaries.
- Independent review work uses a separate bounded worker pool. The standard research pass can dispatch up to ten provider tasks concurrently, while peer-review work can dispatch up to six. Live bot activity panels refresh every three seconds while the page is visible. Actual throughput depends on provider capacity, network latency, rate limits and available compute.
- Parallel execution does not bypass source checks, safety review or human oversight.

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

## API

- `GET /api/agent-identities` returns the role profiles and counts of recorded persistent activity.
- The registry methods support append-only memories and evidence-linked collaboration events. No public write endpoint is enabled for these records.

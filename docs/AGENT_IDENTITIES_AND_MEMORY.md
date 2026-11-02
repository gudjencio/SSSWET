# Persistent research-agent identities

SSSWET agents have stable role-associated profiles with distinct names, specialties, temperaments, communication styles, working methods, strengths and known limitations.

## Identity and memory boundaries

- A profile is a communication and task-allocation aid, not a claim that an agent is a human being.
- Persistent memories are append-only work notes. Each note must include an agent ID, role, content and a reference to the task or source that supports it.
- Collaboration history records observable events such as peer review, joint analysis, disagreement, correction and support.
- The system does not infer friendship, hostility, affection, loyalty or other emotional states from work interactions.
- Agents must not claim to remember events unless the corresponding record is available.
- Memory records do not establish scientific validity. Sources and claims remain subject to independent review.

## Initial research team

The initial profiles include Mira Solène (cross-disciplinary research), Elias Varenne (independent verification), Nadia El-Karim (health research), Theo Marchand (materials science), Asha Okafor (data analysis), Jun Park (systems engineering), Amara Diallo (ethics and accessibility), and Leon Wu (foresight).

## API

- `GET /api/agent-identities` returns the role profiles and counts of recorded persistent activity.
- The registry methods support append-only memories and evidence-linked collaboration events. No public write endpoint is enabled for these records.

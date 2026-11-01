# SSSWET

**Super Soldier Space Warping Engineering Tech**  
*French interface name: Équipements et technologies de distorsions spatiales pour super-soldats (ETDESS).*

SSSWET is an experimental, open research-software project for organizing scientific inquiry, computational studies, evidence review and collaboration between specialized research agents.

The project explores a disciplined workflow for turning research questions into structured work, comparing approaches, documenting evidence and identifying what still needs to be tested. Ambitious scientific ideas are treated as hypotheses—not as established capabilities.

See [research contributions and future technology availability](docs/CONTRIBUTIONS.md) for the contribution process and the conditions governing any future product offer or delivery.

## Monthly PayPal contributions

The contribution interface uses the PayPal subscription plan `P-75A66386EX5825057NLTZHII`. The base plan is USD 1 per month. The interface asks the supporter for a monthly amount in USD (minimum USD 1, adjustable to the cent) and passes that value as the subscription `quantity`, so a quantity of 12 is intended to bill USD 12 per month.

**Important PayPal plan requirement:** PayPal supports custom subscription quantities only when the billing plan has `quantity_supported: true`. PayPal's plan API defaults this field to `false`. Confirm that the live plan has quantity support enabled before advertising variable monthly amounts. If it is disabled, PayPal may reject quantities above 1; in that case, the plan must be recreated or updated using a quantity-supported pricing configuration. The PayPal SDK snippet alone, with `quantity: 1`, does not prove that custom quantities are enabled.

The supporter approves the recurring subscription through PayPal. It is billed monthly until cancelled through PayPal. The interface does not collect card details or claim that a payment has succeeded before PayPal calls the approval callback. The subscription amount is denominated in USD; PayPal may display local currency or conversion information during checkout.

## Contribution model

The previous one-time and manually scheduled instalment interface has been replaced by the monthly PayPal subscription flow described above. The optional legacy Apps Script reminder module is not used by the current website checkout.

## Project goals

- Organize research objectives into manageable tasks and specialist roles.
- Support literature discovery and local document analysis.
- Preserve source provenance and research history.
- Represent hypotheses, findings, sources, datasets and experiments in a knowledge graph.
- Identify research gaps and recorded contradictions for further review.
- Plan experiments and keep simulations distinct from real-world observations.
- Compare computational models and propose bounded follow-up scenarios.
- Coordinate research campaigns, resources and knowledge transfers.
- Provide a multilingual web interface and a local research environment.

## Research programme prioritisation

The local dashboard includes a transparent, human-entered assessment workflow for all 32 research programmes. Six weighted criteria cover societal benefit, ecological and animal benefit, evidence maturity, technical feasibility, resource accessibility, and safety and legal readiness. Incomplete assessments remain visible but are excluded from ranking; previous submissions are preserved in append-only local SQLite history. Each entry requires a reviewer label and written rationale, with optional evidence references. Rankings are advisory decision-support indicators only: they do not establish scientific validity, authorize experiments, allocate funding or certify product readiness. See [research programme prioritisation](docs/RESEARCH_PRIORITISATION.md).

## Reproducibility intelligence

The read-only reproducibility intelligence service summarizes recorded comparisons by protocol and exposes a transparent five-part evidence-completeness index. Matching outputs do not count as independent verification unless that verification is explicitly recorded. Missing comparisons produce no score, and parameter sensitivity remains unassessed until normalized sweep metadata exists. The index is not a measure of scientific truth or validity. See [the reproducibility intelligence documentation](docs/REPRODUCIBILITY_INTELLIGENCE.md).

## Pairwise parameter interaction planning

Published protocols can explicitly nominate pairs of parameters for balanced two-factor factorial study proposals. The read-only planner builds bounded scenario grids from declared factor levels, holds other parameters at their baselines, and reports incomplete definitions rather than guessing. It does not estimate interaction effects, assign run order, establish causality, or execute studies. See [pairwise parameter interaction planning](docs/PARAMETER_INTERACTION_PLANNING.md).

## Parameter sensitivity planning

Published laboratory protocols can carry explicit parameter ranges, units, baseline values, measurement uncertainty, replicate counts and safety constraints. The read-only sensitivity planner turns complete metadata into a one-factor-at-a-time scenario matrix for human review. Missing definitions remain visible instead of being guessed. The planner does not estimate causal effects or parameter interactions, create tasks, execute experiments or establish scientific validity. See [parameter sensitivity planning](docs/PARAMETER_SENSITIVITY_PLANNING.md).

## Research Integrity & Ethics Framework

The append-only risk register records concerns involving data integrity, bias, conflicts of interest, reproducibility, safety, ethics, legal/regulatory constraints and security. Unresolved high or critical risks generate a human-review campaign-hold recommendation. The software does not automatically suspend campaigns, authorize research or certify that a risk has been eliminated. See [the framework documentation](docs/RESEARCH_INTEGRITY_ETHICS.md).

## Scientific Review Board

Structured dossier reviews can record support, challenge, mixed or abstaining assessments, together with a methods assessment, limitations and an explicit conflict-of-interest declaration. Each assessment remains independently visible; disagreement is reported rather than averaged into an automatic verdict. Reviewer labels and conflict declarations are self-reported, and the board does not certify identity, expertise, independence or scientific validity. See [the Scientific Review Board documentation](docs/SCIENTIFIC_REVIEW_BOARD.md).

## Verification review lifecycle

Verification checks can receive append-only human review events with `pending`, `in_progress`, `completed` and `blocked` tracking. Notes and reviewer labels are retained in an immutable event history. The local review-write endpoint is restricted to loopback requests; reviewer labels are self-declared and are not an authentication mechanism. See [the lifecycle documentation](docs/LAB_VERIFICATION_PLANNING.md).

## Laboratory verification planning

The local review API can generate evidence-linked checklists for recorded laboratory discrepancies. These checklists highlight missing records and comparison checks for human assessment; they do not create tasks, execute experiments or establish scientific validity. See [Laboratory verification planning](docs/LAB_VERIFICATION_PLANNING.md).

## Current capabilities

| Area | Available functionality |
|---|---|
| Research workflow | Task decomposition, role-based allocation, strategy changes and bounded orchestration |
| Literature discovery | Crossref, OpenAlex and arXiv metadata discovery; review-oriented duplicate and topic-overlap watch |
| Local documents | JSON corpus and page-based PDF text extraction |
| Model integration | Configurable OpenAI-compatible chat-completions provider |
| Research memory | Persistent collective notes and immutable, versioned scientific-memory snapshots linked to campaigns, graph nodes, experiments and sources |
| Evidence provenance | DOI, dataset and provenance-group records |
| Knowledge graph | Typed nodes and explicit relationships |
| Research review | Gap analysis and contradiction reporting |
| Interdisciplinary discovery | Explainable cross-campaign relation suggestions and unified research-opportunity synthesis for human review |
| Experimentation | Structured plans, simulation records and real-observation records |
| Simulation studies | Bounded multi-model comparisons and reproducible output records |
| Optimization | Human-reviewed adaptive scenario proposals |
| Campaign coordination | Pipeline-integrated milestone scheduling, specialist allocation, resource quotas, retry tracking and explicit completion review |
| Web interface | Responsive multilingual interface, global dashboard, knowledge-network visualization and expandable research-opportunity reviews |

Capabilities are implemented incrementally. The public web interface is static, while the Python research engine runs locally on the operator's computer. The browser can discover that loopback engine from the official GitHub Pages and Google Sites origins when it is running and the browser permits local-network access; GitHub Pages does not host the engine or its SQLite data.


The global dashboard visualizes a bounded view of recorded knowledge-graph
nodes and declared edges, and lists research-gap and interdisciplinary-link
opportunities with their graph and campaign references. These are review
leads only: the dashboard does not infer missing scientific relationships,
create tasks or validate claims. The live dashboard requires the local Python service. When the public page is opened in a browser on the same computer as that service, the interface attempts a restricted cross-origin connection to `127.0.0.1:8765`; Chrome and other browsers may ask for local-network access. If the engine is unavailable or permission is denied, the interface switches to offline guidance and retries automatically. A static Pages deployment does not host or expose the local SQLite research state. See [research opportunity synthesis](docs/RESEARCH_OPPORTUNITIES.md).

## Architecture

The repository is organized into two main parts:

- **`core/`** — Python research engine, command-line tools, local API, persistence, verification and simulation utilities.
- **`web/`** — static multilingual web application and progressive web app assets.

The local service binds to `127.0.0.1` by default and exposes read-oriented API endpoints plus narrowly scoped, loopback-restricted append-only review and assessment submissions. Research state is stored locally in SQLite unless another database path is configured.

## Getting started

### Requirements

- Python 3.11 or newer
- Git
- Node.js 22 or newer for web-interface checks

### Install the research core

```bash
git clone https://github.com/gudjencio/SSSWET.git
cd SSSWET/core
python -m pip install -e .
ssswet-local
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) in a browser.

### Run a research task

```bash
ssswet-run --objective "Review methods for measuring wave propagation" --domain physics

# Run a one-shot scholarly metadata watch
ssswet-watch --query "wave propagation measurement methods"
```

A local JSON corpus can be supplied with `--corpus`. PDF extraction is available through the optional dependency:

```bash
python -m pip install -e ".[pdf]"
ssswet-run --objective "Compare experimental methods" --domain physics --pdf ./paper.pdf
```

For literature metadata discovery, use `--provider crossref`, `openalex`, `arxiv` or `literature`. A compatible language-model provider can be configured with local environment variables; API credentials must never be committed to the repository.

The literature watch compares returned metadata with registered sources and collective-memory topics. It flags possible DOI duplicates, close title matches and related memory entries for review; it does not automatically import sources, alter campaigns or validate claims. Saved reports are available through the local read-only `/api/literature-watch` endpoint.

### Continuous research and success notifications

Autonomous research starts automatically when the local interface is launched with `ssswet-local`. A background worker begins a complete pass across all 32 technology programmes and repeats it every 60 minutes by default. The worker runs alongside the interface, so no separate daemon command is required for normal operation.

To change the interval, set `SSSWET_RESEARCH_INTERVAL_MINUTES` before starting the local service, or pass `--research-interval-minutes`. To run the interface without background research, pass `--disable-background-research`.

The standalone research daemon remains available for dedicated use:

```bash
ssswet-research
```

The daemon performs a research cycle every hour by default. To run one cycle only:

```bash
ssswet-research --once
```

The optional Google Apps Script relay sends one concise email after a cycle containing successfully completed programmes. Failed or interrupted programme runs are not included, and notification failures do not cause completed research to be repeated. The relay does not transmit private user data or internal agent deliberations.

To enable notifications:

1. Deploy the Apps Script project as a web app that executes as the project owner. Set access according to the intended deployment and keep the shared-secret check enabled.
2. In Apps Script **Project Settings → Script properties**, set `SSSWET_RELAY_SECRET` to a randomly generated secret of at least 32 characters.
3. On the computer running SSSWET, configure the web-app deployment URL and the same secret as environment variables. In PowerShell:

```powershell
$env:SSSWET_RELAY_URL = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
$env:SSSWET_RELAY_SECRET = Read-Host "Enter the SSSWET relay secret"
ssswet-research
```

Keep the secret out of source files, commits, screenshots and public issue reports. Do not place it in the website's JavaScript. If either environment variable is missing, research continues normally and email notifications remain disabled. The relay requires HTTPS.

See the [core developer guide](core/README.md) for command options, provider configuration, data formats and API details.

## Scientific integrity and responsible research

SSSWET is a research-support tool, not an authority on scientific truth. Its outputs may be incomplete, inaccurate or biased.

- Model agreement is not proof, and generated text is not a scientific source.
- Bibliographic discovery does not establish the validity of a publication or claim.
- Provenance indicators support review; they do not automatically establish source independence.
- Simulation outputs are not real-world observations.
- Optimization scores are not probabilities, confidence intervals or proof of an optimum.
- Verification states require explicit evidence and review; they are not inferred from presentation or consensus.
- Medical, biological, aerospace and other safety-critical work requires qualified domain experts, appropriate ethics review and all applicable legal and regulatory approvals.
- The project does not provide instructions for weapon construction or intentional harm.
- Physical experiments are not launched automatically. High-impact actions require human authorization.

The project aims to make uncertainty, limitations, provenance and unresolved questions visible rather than conceal them.

## Languages

The web interface currently includes initial catalogues for English, French, Spanish, German, Italian, Portuguese, Dutch, Russian, Ukrainian, Arabic, Hebrew, Japanese, Korean, Chinese and Hindi.

Arabic and Hebrew use right-to-left layout. Translation coverage and quality are evolving; contributions from fluent speakers are welcome.

## Public links

- **Web application:** [gudjencio.github.io/SSSWET](https://gudjencio.github.io/SSSWET/)
- **Source code:** [github.com/gudjencio/SSSWET](https://github.com/gudjencio/SSSWET)
- **Google Sites mirror:** [sites.google.com/view/ssswet](http://sites.google.com/view/ssswet)
- **X:** [@ssswetech](https://x.com/ssswetech)
- **Instagram:** [@ssswetech](https://www.instagram.com/ssswetech)
- **YouTube:** [@ssswetech](https://www.youtube.com/@ssswetech)
- **Contact:** [ssswetindustries@gmail.com](mailto:ssswetindustries@gmail.com)

The Google Sites mirror is already published and embeds the canonical web application. Visitors can open it directly; no setup is required.

## License

SSSWET is distributed under the [MIT License](LICENSE). The license permits use, modification and redistribution subject to its terms.

## Development and contributions

Bug reports, reproducible test cases, documentation improvements, accessibility work and translation reviews are welcome through the repository's issue tracker and pull requests.

Please do not publish API keys, private datasets, personal information or confidential research material in issues or commits. Contributions should include relevant tests and clearly distinguish measured results, simulations, assumptions and hypotheses.

## Project status

SSSWET is under active development. Interfaces, APIs and data formats may change between releases. Features described as available are implemented in the repository, but their scientific usefulness depends on the quality of supplied data, methods and independent review.

---

**Project:** SSSWET  
**French designation:** ETDESS  
**Contact:** ssswetindustries@gmail.com


Campaign-specific literature monitoring can be configured for active campaigns
and run on a recurring schedule with `ssswet-watch-campaigns`. The command
processes due subscriptions once; use an operating-system scheduler for
periodic invocation. Monitoring reports newly seen and previously seen
bibliographic identifiers without automatically modifying research memory
or campaign state. See the core developer guide for configuration details.


SSSWET also provides explainable cross-campaign collaboration suggestions.
The local read-only endpoint `/api/collaboration/recommendations` lists
knowledge-graph items that may be relevant to other active campaigns. A
suggestion never creates a transfer or validates a finding; an operator must
explicitly initiate a hand-off for review. See the core developer guide.


A scientific dispute review workflow is also available through the local
`/api/disputes` endpoint. It records human assessments of explicit graph
contradictions without automatically choosing a winning claim or changing
scientific verification states.


## Digital-lab discrepancy review

The local read-only endpoint `/api/lab-discrepancies` screens recorded comparisons for result divergences, incompatible conditions and incomplete comparison records. A divergence is only a review lead: it does not prove a scientific contradiction, identify a correct result or change verification states. See [the review guide](docs/LAB_DISCREPANCY_REVIEW.md).


## Versioned scientific memory

The local research core includes an append-only scientific-memory ledger. Each entry is a versioned snapshot linked, where applicable, to campaign identifiers, knowledge-graph nodes, experiment plans and source identifiers. Revisions require an explicit superseded version and a review note; earlier snapshots remain in the archive.

The read-only local endpoint `/api/scientific-memory` provides the version history and current-entry overview. Add `?q=...` for transparent lexical retrieval. The companion `/api/scientific-memory/suggestions` endpoint surfaces linked graph contradictions and recorded research gaps as review leads. A contradiction marks linked entries for attention but does not select a correct claim. Older versions are retained and labelled as potentially outdated rather than deleted.

Workflow states (`candidate`, `reviewed`, `contested`, `archived`) are not scientific verification states. Retrieval scores, review decisions and graph relationships do not establish scientific validity. Suggestions do not create tasks or launch experiments automatically. See the [core developer guide](core/README.md) for the Python API.


## Research timeline

The local research engine exposes a derived chronology at `/api/research-timeline`.
It combines dated knowledge-graph records and relationships, scientific-memory
versions, experiment-plan updates and records, literature-watch reports,
dispute-review activity, and campaign updates. Use
`/api/research-timeline?campaign_id=...` to focus on one campaign and
`?limit=...` to bound the response.

Only records with an explicit, parseable timestamp are included. The timeline
preserves event types and references so that a simulation, observation,
literature lead, memory revision, or contradiction review is not flattened
into the same kind of result. Chronological order is not scientific validation;
the endpoint is read-only and never starts work automatically.


## Cross-campaign peer review

Research campaigns can request a structured review of a knowledge-graph item by one or more other active campaigns. Reviewers submit an outcome (supports, challenges, inconclusive, or unable_to_assess), an assessment, a method, optional source identifiers, limitations, and an explicit independence declaration.

The local read-only endpoint /api/collaboration/peer-reviews reports requests and submissions. The dashboard summarizes open and completed reviews. Review submissions are append-only; one submission is accepted per assigned reviewer campaign and request. Peer-review activity also appears in the research timeline.

Review reports also provide a descriptive synthesis: mixed or unanimous outcome patterns, distinct methods, repeated source identifiers, repeated provenance groups, and submitted limitations. This is a transparency aid, not a vote or an adjudication.

An independence declaration is self-reported and is not independently authenticated. Different campaign identifiers do not prove independent personnel, data, methods, or funding. Review outcomes are recorded perspectives, not votes that establish truth. No review automatically changes a knowledge node's verification state or resolves a scientific dispute.


## Shared digital laboratory

The local research core includes a shared digital-laboratory registry for reviewed protocol versions and recorded executions. A protocol is published only with a named reviewer, review note, explicit procedure, required parameters, expected outputs, controls, and limitations. Published protocol versions and execution records are immutable and carry SHA-256 content fingerprints.

A separate research campaign can record a reproduction attempt against a published protocol version. Each run retains its execution kind (simulation or real-world observation), exact parameters, outputs, method, environment, model/code reference, provenance group, limitations, and an explicit independence declaration. SSSWET does not execute uploaded protocols or physical experiments.

The read-only endpoint /api/digital-lab exposes protocol and run records. The research timeline includes publication and run-recording events. Run comparisons require the same protocol version, execution kind, and exact parameters; numeric outputs can be compared using an explicitly supplied tolerance. Differences are reported field by field, and comparison reports are stored immutably with source and dataset references. Independent reproduction candidacy requires distinct campaigns, self-declared independence from both teams, distinct non-empty provenance groups, and no shared source or dataset identifiers. Independence is not independently authenticated.

Agreement is not scientific validation. The comparison does not select a winning model, certify the methods, or change any knowledge verification state. Simulations and real observations are never mixed as equivalent evidence.


See [Interdisciplinary relation discovery](docs/INTERDISCIPLINARY_RELATIONS.md) for the local API and review boundaries.


The digital laboratory also exposes a read-only cross-campaign reproduction matrix at `/api/digital-lab/reproduction-matrix`. It groups runs by exact protocol version and identifies cross-campaign pairs awaiting comparison. Run comparisons report environment and code/model-reference differences explicitly; the matrix does not execute experiments or certify reproduction.


Protocol improvement proposals can be submitted and reviewed through the local Python service. The read-only queue is available at `/api/digital-lab/proposals`. Only the active campaign that owns the published protocol can accept or reject a proposal. Acceptance publishes a new immutable protocol version; rejection preserves the existing version. Proposal events retain the rationale and review note. This workflow is not scientific validation.


## Descriptive laboratory statistics

SSSWET can produce read-only descriptive summaries of recorded numeric laboratory outputs, grouped by protocol version and output field. Reports include sample size, mean, median, range, sample standard deviation, quartiles and potential outlier review flags. Values are never silently removed, and the summaries do not establish statistical significance, causality or scientific validity. See [descriptive laboratory output statistics](docs/LAB_STATISTICAL_SUMMARIES.md).


The [public research portfolio](docs/CONTRIBUTIONS.md#public-research-portfolio-and-progress-records) explains how research stages, confirmed contribution totals, funding goals and future availability are reported transparently.


## Research journal

The local research engine includes an append-only, hash-chained journal for dated technology-programme updates. Entries retain explicit classifications (hypothesis, literature, simulation, prototype, observation, independent review or project update), evidence references and progress states. The journal API reports chain integrity separately from scientific validity. Local journal writes are restricted to loopback clients; the static public site does not accept remote submissions.


## Technology Feasibility Observatory

The local research engine includes a read-only observatory for all 29 technology programmes. It summarizes explicitly recorded literature, simulations, prototypes, tests and independent reviews, then identifies missing review areas without inventing a feasibility score or authorizing delivery. See [the observatory documentation](docs/TECHNOLOGY_FEASIBILITY_OBSERVATORY.md).


## Private Gmail delivery workflow

The owner-restricted [Google Apps Script source and setup guide](integrations/gmail-delivery-control/README.md) supports manual payment-and-delivery verification and creates institutional email drafts without sending them automatically.

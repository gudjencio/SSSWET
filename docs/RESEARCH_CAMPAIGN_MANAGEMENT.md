# Research Campaign Management

SSSWET research campaigns turn a research priority into a bounded, reviewable work plan. Campaign records are stored by the research store and can be coordinated with role-based resource scheduling.

## Required campaign design

Every new campaign must include:
- a clear objective and domain;
- one or more milestones with measurable objectives;
- explicit success criteria and failure criteria;
- at least one safety gate.

Campaigns may additionally record a falsifiable hypothesis, responsible specialist roles, resource requirements, source references and further safety gates. Missing information must remain explicit rather than being fabricated.

## Workflow

1. Draft the campaign and define its question, hypothesis and milestones.
2. Attach evidence references and define what would count as success or failure.
3. Obtain qualified safety, ethics, legal and domain review appropriate to the work.
4. Activate the campaign only after the required review.
5. Queue bounded subtasks against milestones using the campaign coordinator.
6. Record outcomes, negative results, corrections and independent reviews.
7. Continue, revise, pause, block or complete the campaign based on recorded evidence.

The coordinator schedules tasks and records resource assignments. It does not itself perform laboratory work, operate medical equipment, conduct experiments, or certify findings.

## API

```python
from ssswet_core.campaigns import CampaignMilestone, create_campaign

campaign = create_campaign(
    campaign_id="example-campaign",
    title="Example research campaign",
    objective="Answer a narrowly defined research question",
    domain="materials",
    milestones=[
        CampaignMilestone("m1", "Evidence review", "Assess the published evidence"),
        CampaignMilestone("m2", "Model comparison", "Compare documented model assumptions"),
    ],
    hypothesis="A falsifiable, evidence-linked hypothesis.",
    success_criteria=("Pre-registered result threshold is met",),
    failure_criteria=("Independent assessment does not meet the threshold",),
    agent_roles=("general_researcher", "independent_verifier"),
    resource_requirements=("Documented compute budget",),
    source_refs=("https://example.org/relevant-review",),
    safety_gates=("Qualified domain and safety review before practical work",),
)
```

The identifiers and values above are illustrative. They do not represent an approved experiment or an actual finding.

## State and interpretation

Campaign states track workflow progress: draft, active, paused, completed or blocked. Milestone states track pending, in-progress, completed or blocked work. Completion requires every milestone to be marked completed.

Campaign completion is administrative; it does not mean the hypothesis was confirmed or that a technology is validated. Results must remain classified as observations, simulations, interpretations or independently reproduced findings.

## High-risk and biomedical research

Biomedical, human-subject, animal, clinical, genetic, chemical, radiological and other high-risk research requires the applicable qualified leadership, ethics review, biosafety review, regulatory authorization and informed consent. A campaign record is not permission to perform an experiment or provide treatment. Emergency care must never be delayed or replaced by speculative research.

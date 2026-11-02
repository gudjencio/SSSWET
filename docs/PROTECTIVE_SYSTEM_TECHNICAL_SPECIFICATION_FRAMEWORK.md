# Protective System Technical Specification Framework

**Status:** Research and feasibility framework. It does not certify, rate or authorize any product.

## Purpose

SSSWET uses this framework to compare protective equipment and assistive exoskeleton concepts without confusing a design target with demonstrated performance.

## Required specification fields

| Field | Requirement |
|---|---|
| Model | Stable public identifier and revision |
| Intended use | Defined occupational, rescue, civil-protection or other lawful use |
| Hazard envelope | Specific hazards and excluded hazards |
| Protection target | Measurable target, never an implied rating |
| Mass | Target and measured values when available |
| Mobility | Range of motion, dexterity and task constraints |
| Thermal burden | Heat retention, ventilation and environmental limits |
| Power | Battery or other energy requirements, runtime and safe shutdown |
| Materials | Traceable candidate materials and relevant properties |
| Maintainability | Inspection, repair, replacement and service intervals |
| Safety | Fail-safe behavior, emergency removal and failure modes |
| Human factors | Fit, fatigue, comfort, accessibility and training burden |
| Cybersecurity | Security boundaries for connected or sensor-equipped systems |
| Evidence | Tests, standards, peer review and independent verification |
| Cost | Low/base/high scenario with documented inputs |
| Maturity | Concept, feasibility, prototype, tested, independently verified or certified |

## Standard comparison model

Each candidate receives three separate values where evidence permits:

- **Target:** what the research programme intends to achieve.
- **Observed:** what has actually been measured under stated conditions.
- **Verified:** what an independent reviewer or test organization has confirmed.

An unknown value remains `unknown`; it is never estimated merely to complete a table.

## Protection categories

### Impact and mechanical protection

Describe the exact test method, coverage, configuration and conditions. Terms such as “bulletproof”, “blast-proof” or “military-grade” are prohibited unless a competent independent test establishes the claim for the exact configuration and applicable standard.

### Environmental protection

Document temperature range, moisture, particulate exposure and any chemical hazards separately. One environmental rating must not be generalized to unrelated hazards.

### Thermal protection

Track insulation, heat dissipation, metabolic burden, duration and emergency removal. Greater protection can increase heat retention and reduce mobility; both effects must be measured.

### Exoskeleton assistance

Measure assistance, task duration, energy consumption, fit, balance, failure behavior and musculoskeletal effects. A higher assistance setting is not automatically safer or better.

## Cost model

The pricing model must separate:

1. materials and components;
2. engineering and specialist review;
3. prototype fabrication;
4. independent testing and certification;
5. sensors, computing and power systems;
6. training and fitting;
7. maintenance, repair and replacement;
8. logistics and lifecycle support;
9. applicable taxes and fees.

Low/base/high scenarios must include assumptions, evidence references, timestamps and uncertainty. If a required cost input is unavailable, the scenario is marked incomplete rather than invented.

## Version tiers

### Standard

Prioritizes affordability, maintainability and broad lawful occupational use.

### Reinforced

May use higher-durability components, additional environmental testing, redundant safety features or longer service life when evidence and cost justify them.

### Extreme

Reserved for narrowly defined environments with unusually demanding requirements. A higher price is justified only by documented engineering, materials, testing, certification and lifecycle-support costs.

## Non-offensive boundary

The framework explicitly excludes weapon design, weapon optimization, targeting systems, offensive autonomy and weapon integration. Protective equipment may be evaluated for lawful military, emergency-response, civil-protection and occupational applications, subject to applicable law, procurement controls, end-use review and independent safety oversight.

## Evidence gate

A system may progress from concept to prototype planning only after its intended use, hazards, safety assumptions and measurable test plan are defined. A system may not be described publicly as certified, combat-ready, bulletproof, blast-proof, chemical-proof or radiation-proof without corresponding independent evidence.

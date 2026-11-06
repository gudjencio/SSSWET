# SSSWET research portfolio: ten super-categories

The public research catalogue is presented as ten expandable collections of 100 programmes each. The complete portfolio contains 1,000 unique research-programme records.

## Collections

1. Space science & exploration
2. Protection, rescue & resilience
3. Energy & power systems
4. Advanced materials & manufacturing
5. Health, biology & human support
6. Environment, climate & ecosystems
7. Robotics, autonomy & mobility
8. Computing, knowledge & society
9. Sensing, monitoring & forecasting
10. Systems integration & reliability

The browser originally exposed 500 entries (488 expansion programmes and 12 curated programmes). The grouping layer restores the 106 canonical records already present in the Python core registry, then adds the 394 deterministic programmes from the core expansion algorithm. This gives 606 existing/canonical records plus 394 generated records. The first eight collections preserve all 606 records in their original eight domains and top up each domain with generated domain-specific programmes until it contains 100 entries. The remaining 200 generated programmes are divided into two cross-domain collections using title and capability keywords. Stable identifiers are retained and each programme appears exactly once.

## Interface behaviour

- All ten collections start collapsed.
- A collection renders its cards only when opened.
- Global search scans all 1,000 entries and opens only collections with matching records.
- Search results retain the existing data-tech action contract used by the contribution dialog.
- The existing catalogue remains in place if the grouping integrity check fails.
- The interface reports the count as research programmes, not validated technologies.

## Validation and limitations

The grouping function checks for exactly 1,000 unique identifiers, ten groups, 100 entries per group and no duplicate assignment. The Node regression test checks the 500 browser-visible entries, the 106 canonical Python registry entries, and the 394 deterministic generated entries against the 606 stable taxonomy identifiers.

The two cross-domain collections are a navigation aid based on programme titles and capability terms. They do not replace the authoritative domain and subcategory metadata, change scientific status, or imply that any programme has been validated. The catalogue remains a set of research objectives; inclusion is not evidence of feasibility, readiness, safety or demonstrated performance.
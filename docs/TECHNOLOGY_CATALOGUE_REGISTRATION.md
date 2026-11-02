# SSSWET technology catalogue registration

The machine-readable research catalogue uses the same stable technology identifiers as the public web taxonomy. Each entry records its category and subcategory and can be registered as a persistent research dossier.

Registration is idempotent: running it again does not duplicate existing dossiers. New entries begin in the `concept` state and explicitly carry `research_status: not_assessed`. Catalogue presence is not evidence of active research, feasibility, validation, a prototype, or a product.

The current catalogue contains 100 technology identifiers. The registry reports the number created and already present on each run.

Implementation: `core/ssswet_core/technology_catalogue.py`.

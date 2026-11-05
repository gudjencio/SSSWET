# SSSWET performance improvements — 2026-11-05

This update focuses on avoiding unnecessary work in the public interface and
reducing sort work in the persistent research-memory store.

## Interface

- Catalogue localization caches the catalogue root and updates only newly
  inserted cards after DOM mutations.
- Added catalogue nodes are collected and processed once per animation frame.
- The previous repeated full-document text scan has been removed.
- Catalogue cards use `content-visibility: auto` with an intrinsic size so
  offscreen cards can skip layout and paint until they approach the viewport.
- Agent avatar animation no longer requests a dedicated compositor layer for
  every avatar.
- Engine status polling now runs every 15 seconds while the page is visible,
  pauses while hidden, resumes on visibility/online events, and backs off up to
  120 seconds when the engine is unavailable.
- Voice controls update on speech events and initial setup rather than polling
  browser speech state twice per second.

## Persistent memory

SQLite now has ordered indexes for:
- global collective-memory recency,
- campaign-scoped recency,
- status-scoped recency,
- combined campaign/status recency.

Query-plan regression tests assert that common retrieval patterns use those
indexes without a temporary sort. Indexes are created idempotently during the
existing schema initialization.

## Measurement policy

These changes reduce known repeated work and enforce query-plan properties.
No percentage speedup is claimed without a reproducible browser/device
benchmark against a recorded baseline. Runtime performance should be measured
on representative low-end mobile and desktop hardware before publishing
numeric claims.

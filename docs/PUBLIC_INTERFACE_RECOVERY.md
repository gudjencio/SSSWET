# Public interface recovery and daily browser watch

## Purpose

The SSSWET public site is a static GitHub Pages application. Its public shell must remain usable when the hosted research API is unavailable, and a stale service-worker cache must not conceal a newly published interface.

## Change summary

- The service-worker cache namespace advances from `ssswet-web-v190` to `ssswet-web-v191`.
- Installation caches the small application shell assets independently. A transient failure of one cache request no longer prevents the successor worker from installing.
- The successor worker activates promptly and claims open clients.
- Same-origin GET requests use network-first retrieval. A successful network response refreshes the cache; a network failure falls back to the matching cached response and then the cached application shell for navigations.
- Previous SSSWET cache namespaces are removed after activation to prevent old bundles from silently remaining authoritative.

## Acceptance criteria

1. A new worker can install even if one optional asset request fails.
2. After activation, a navigation attempts the deployed network version before using an offline fallback.
3. Same-origin scripts and styles are not permanently pinned to a stale cache-first response.
4. If the network is unavailable, a previously cached shell can still open.
5. The public page renders its main shell, catalogue and language selector.
6. A visitor can change the language, activate the research refresh control, open the report UI, and open a technology detail dialog.
7. The Virtual Time Travel Mapping entry point remains present.
8. No real report submission, purchase, payment, account change or external transaction is performed by the smoke test.

## Daily browser verification

`.github/workflows/public-interface-watch.yml` runs a Chromium browser check once per day and on manual dispatch. It records a JSON report and screenshot as a 14-day artifact. A failure opens or updates one diagnostic GitHub issue with a link to the run. The workflow does not merge code or deploy a repair.

## Comparison with previous behaviour

| Area | Previous behaviour | New behaviour |
|---|---|---|
| Cache policy | Cache-first for every same-origin GET | Network-first with offline fallback |
| Worker installation | One failed asset in `cache.addAll` could abort installation | Independent core-shell cache attempts |
| Activation | Waiting for prior clients could delay activation | Prompt activation and client claim |
| Browser verification | CI mostly validated source files and unit tests | Real Chromium visit and interaction checks against the published URL |
| Failure evidence | No public-site screenshot/report | JSON report, screenshot and incident issue |

## Limitations

- A scheduled GitHub Actions workflow is not a continuous uptime guarantee; GitHub may delay scheduled runs.
- The browser watch checks Chromium on a GitHub-hosted Linux runner, not every browser, mobile device, embedded Google Sites context or visitor network.
- The workflow must be merged into `main` before GitHub's schedule will run for the default branch.
- The first successful browser run is still required to establish the deployed result. A source change or green unit tests alone do not prove that GitHub Pages has published it.
- Offline fallback is only available for assets that were previously cached successfully.

# Repeatable browser performance benchmarks

SSSWET runs an advisory Chromium benchmark against the locally served public
web interface. The workflow runs for pull requests targeting `main`, on
manual dispatch, and weekly.

## Measurements

Each run performs three trials at desktop (1440 × 900) and mobile (390 × 844)
viewports. Each trial records:

- cold navigation and a warm reload in the same browser context;
- navigation response, DOM-content-loaded and load timings;
- First Contentful Paint and a sampled Largest Contentful Paint;
- Cumulative Layout Shift and observed long tasks;
- DOM node count and live catalogue card count;
- append/layout stress probes with 100, 500 and 1,000 cloned catalogue cards;
- environment, commit and workflow-run metadata.

The JSON report is uploaded as a GitHub Actions artifact for 90 days. It can
be downloaded from the workflow run's **Artifacts** section.

## Interpretation and safeguards

These are controlled laboratory observations, not field-user telemetry.
GitHub-hosted runners use virtual hardware; the mobile viewport is emulation,
not a physical phone. LCP is sampled after a fixed settling interval. The
catalogue scale test clones an existing card and is a synthetic stress probe.

No hard performance threshold is enforced yet. First collect comparable
measurements across multiple runs and inspect variance. Only then should
regression thresholds be introduced. Do not compare runs across materially
different runner or browser environments as if they were identical.

The benchmark does not transmit visitor data, does not contact the hosted
research engine, and does not submit forms or perform payment or contribution
actions. It uses a local static server and disposable browser contexts.

## Reproduce locally

Install Python and Playwright, install Chromium, then serve the public UI:

```bash
python -m pip install playwright
python -m playwright install chromium
python -m http.server 8765 --directory web
```

In another terminal:

```bash
python .github/scripts/performance_benchmark.py --url http://127.0.0.1:8765/ --trials 3
```

The default output is `performance-results/benchmark.json`.

# Hosted deployment

SSSWET can run as a hosted service independently of a visitor's computer. The repository includes a Render Blueprint and Docker image for a continuously running API with a persistent SQLite disk.

## Deploy

1. Sign in to Render and create a new Blueprint from this repository.
2. Review the generated service **ssswet-research-api** before confirming deployment.
3. The Blueprint uses a paid 0.5 CPU / 512 MB instance and a 1 GB persistent disk. Confirm the current price in Render before approving; the service is not deployed merely by committing these files.
4. Wait for the service health check at `/api/status` to pass.
5. The public interface is configured for `https://ssswet-research-api.onrender.com`. If Render assigns a different hostname, update `web/api-config.js` to the exact service URL and commit the change.
6. GitHub Pages deploys the updated static interface automatically after the web files change. Google Sites should continue embedding the GitHub Pages interface.

## Runtime and data

The service binds to Render's assigned port, runs the existing hourly autonomous research worker, and stores its research database and private order register under the persistent disk mount at `/var/data`. The persistent disk is required: container files outside the disk are ephemeral. Do not deploy the service on a free sleeping instance if uninterrupted background research is required.

The browser-facing API is read-only for public dashboard data. Existing local-only administrative and review-write restrictions remain in place. Do not add secrets, API keys, relay tokens or private credentials to this repository. Configure any future provider credentials as encrypted environment variables in the hosting provider.

A successful deployment is confirmed only when Render reports the service healthy and `https://ssswet-research-api.onrender.com/api/status` returns JSON with `"service":"SSSWET"`. Before that, the public interface may still show unavailable live data.


## Public improvement reports

The public interface includes a localized **Report** control (shown as **Signaler** in French) with a multilingual improvement menu. Submissions are validated by the hosted API and opened as GitHub issues in the SSSWET repository. The intake endpoint never edits repository files or applies a suggestion automatically.

To enable submissions on Render, create a fine-grained GitHub personal access token restricted to `gudjencio/SSSWET` with **Issues: Read and write** permission. Add it to the Render web service as the secret environment variable `SSSWET_GITHUB_TOKEN`. Never place this token in the public website, repository files, browser storage or client-side configuration. Redeploy the service after setting the variable.

Reports are requests for review, not authorization to remove or replace existing project functionality. Any implementation should preserve existing behaviour and pass the automated checks.


## Automated improvement proposals

Public reports labelled `public report` trigger the report-processing workflow. When the repository secret `OPENAI_API_KEY` is configured, the workflow evaluates the request, drafts a narrowly scoped additive patch, rejects deletions and protected paths, runs the core test suite and web-interface checks, and opens a pull request only when all checks pass. Reports that are unclear, destructive, unsafe, or require scientific or human judgment remain available for manual review.

Add `OPENAI_API_KEY` under **Repository Settings → Secrets and variables → Actions**. The key is used only by the private GitHub Actions runner and must never be placed in public files or browser configuration. The workflow uses the repository's temporary `GITHUB_TOKEN` to create a branch and pull request.

Automatic processing does not automatically merge code into the live project. Every generated pull request remains reviewable before integration, preserving a final safeguard against malicious or mistaken public suggestions. The public **View my improvements** menu stores the reports submitted from that browser locally and links to their GitHub issue records.


## Browser-origin policy

The local server defaults to the dedicated GitHub Pages origin for browser access. It does not trust the shared `sites.google.com` origin: every Google Sites property uses that same browser origin, so an `Origin` header cannot distinguish this project's mirror from an unrelated site.

- `SSSWET_ALLOWED_ORIGINS` controls browser CORS access to public read endpoints. Keep this list narrow. The hosted public API may explicitly allow Google Sites for public read-only data, but do not reuse that setting for a local engine exposed on a user's computer.
- `SSSWET_ALLOWED_WRITE_ORIGINS` controls browser-origin write endpoints. The default is `https://gudjencio.github.io`; loopback origins are accepted for the local interface. The shared `sites.google.com` hostname is always rejected for writes, even if it appears in an environment allowlist.
- If a future mirror needs write access, use a dedicated custom domain or a server-side relay with explicit request authentication and abuse controls. Do not add the shared Google Sites origin to the write allowlist.

Origin checks mitigate browser cross-site requests; they are not user authentication and do not replace endpoint-specific authorization.

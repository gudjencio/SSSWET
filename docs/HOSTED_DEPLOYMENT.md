# Hosted deployment

SSSWET can run as a hosted service independently of a visitor's computer. The repository includes a Render Blueprint and Docker image for a continuously running API with a persistent SQLite disk.

## Deploy

1. Sign in to Render and create a new Blueprint from this repository.
2. Review the generated service **ssswet-research-api** before confirming deployment.
3. The Blueprint uses a paid Starter instance and a 1 GB persistent disk. Confirm the current price in Render before approving; the service is not deployed merely by committing these files.
4. Wait for the service health check at `/api/status` to pass.
5. The public interface is configured for `https://ssswet-research-api.onrender.com`. If Render assigns a different hostname, update `web/api-config.js` to the exact service URL and commit the change.
6. GitHub Pages deploys the updated static interface automatically after the web files change. Google Sites should continue embedding the GitHub Pages interface.

## Runtime and data

The service binds to Render's assigned port, runs the existing hourly autonomous research worker, and stores its research database and private order register under the persistent disk mount at `/var/data`. The persistent disk is required: container files outside the disk are ephemeral. Do not deploy the service on a free sleeping instance if uninterrupted background research is required.

The browser-facing API is read-only for public dashboard data. Existing local-only administrative and review-write restrictions remain in place. Do not add secrets, API keys, relay tokens or private credentials to this repository. Configure any future provider credentials as encrypted environment variables in the hosting provider.

A successful deployment is confirmed only when Render reports the service healthy and `https://ssswet-research-api.onrender.com/api/status` returns JSON with `"service":"SSSWET"`. Before that, the public interface may still show unavailable live data.

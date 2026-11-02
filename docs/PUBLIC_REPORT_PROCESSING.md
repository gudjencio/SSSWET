# Public report intake and processing

The public **Report** control submits a validated request to the hosted SSSWET API. The API creates a GitHub issue in the approved repository and returns the issue number and URL to the browser.

## Automatic routing

When a report issue is opened, the GitHub Actions workflow:

1. Adds the `needs-human-review` label so the report is visible in the review queue.
2. Runs the report processor.
3. If `OPENAI_API_KEY` is configured, asks the model for a narrowly scoped additive patch, runs the complete Python test suite and JavaScript syntax/localization checks, and opens a pull request only if all checks pass.
4. Never merges a generated pull request automatically.
5. If the model key is unavailable, or no safe patch can be produced, leaves the report in the review queue and posts an explicit status comment.

The report API requires the Render service environment variable `SSSWET_GITHUB_TOKEN` with permission to create issues in `gudjencio/SSSWET`. The GitHub Actions workflow uses its scoped `GITHUB_TOKEN` for labels, comments and pull requests, and `OPENAI_API_KEY` for automated patch proposals.

## Operational verification

A successful browser submission means the API returned a created GitHub issue number. A visible status label is not proof that a patch was merged. The report history panel retrieves issue and pull-request status from GitHub.

No report is marked as successfully submitted when the API rejects the request. The public UI shows an unavailable or error state instead.

Repository tests mock GitHub's issue-creation response to verify request validation, labels, authorization handling and receipt metadata. This does not substitute for verifying the live Render environment variables or a real end-to-end report submission.

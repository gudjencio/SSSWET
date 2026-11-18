# Public-report patch processor security isolation

The report processor is split into three jobs to avoid executing generated code in a
credential-bearing process.

1. **Prepare:** reads a labelled public issue and approved repository context. The
   model can return a small diff. This job holds the GitHub and model credentials,
   but it never applies or executes the patch. The output is bounded base64.
2. **Validate:** receives only the patch output, has contents: read, and no
   repository secrets. It applies the patch in an ephemeral runner, runs the core
   test suite and web syntax/localization checks, and rejects tracked-file
   mutations made by tests.
3. **Publish:** runs only after validation succeeds. It rechecks the patch scope,
   applies it, commits and opens a PR. It does not execute generated code.

The guard permits at most six edits to existing public code, documentation,
tests, or README, with a 100 KB cap. It rejects file creation/deletion,
renames, mode changes, binary patches, path mismatch, duplicate paths, unsafe
path traversal and finance/payment/tax/refund/subscription/legal-policy,
customer, product-availability and release/distribution files. Changes to
existing test files must be additive (no removed test lines). New test files
are not permitted by the automatic report workflow.

All jobs disable checkout credential persistence. Only the prepare and publish
jobs receive narrowly scoped tokens. The validation job uses a sanitized
environment as defense in depth.

This design reduces credential exposure but is not a general-purpose sandbox.
Generated code still runs on an ephemeral GitHub-hosted runner with read-only
repository permission and no secrets; network egress and runner isolation are
not independently hardened here. Human review remains required before merging.

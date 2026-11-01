# Collaborative digital-lab reproduction tracking

The local research service exposes a read-only reproduction matrix:

`GET /api/digital-lab/reproduction-matrix?limit=200`

The matrix groups recorded runs by exact protocol identifier and version,
lists the campaigns represented in each group, and identifies pairs of runs
from different campaigns that have not yet been compared. It is a review
queue only. It does not execute comparisons, schedule experiments, or
establish independent reproduction.

The standard `GET /api/digital-lab` overview includes the same matrix and a
pending cross-campaign comparison count. Run comparisons additionally expose
whether environments and code/model references match. Environment differences
are recorded field by field for expert assessment; they are not silently
ignored and do not automatically invalidate a run comparison.

An independent-reproduction candidate is not an authenticated independent
reproduction. Shared sources, datasets, provenance, calibration, measurement
uncertainty, model assumptions and domain-specific safety requirements need
human review. Simulation and real-observation records remain distinct.
SSSWET does not execute physical experiments or automatically certify results.

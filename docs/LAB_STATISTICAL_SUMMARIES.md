# Descriptive laboratory output statistics

The local read-only endpoint `GET /api/lab-statistical-summaries` summarizes finite numeric output values already recorded in digital-laboratory runs. The optional `limit` query parameter accepts integers from 1 to 500 and defaults to 200.

Summaries are grouped by protocol ID, protocol version and top-level output name. Each group reports sample size, arithmetic mean, median, minimum, maximum, range, sample standard deviation when at least two values exist, and quartiles/interquartile range. The report also lists a bounded set of run identifiers, distinct campaign count, declared-independence count and recorded provenance groups.

Boolean, non-numeric, non-finite, malformed and unnamed output values are ignored and counted. They are never coerced into numbers. Runs are not merged across protocol versions.

## Potential outliers

For groups with at least four observations, values outside the Tukey 1.5-IQR fences are flagged as potential outlier candidates. The observations remain in every calculation and are not deleted, down-weighted or silently changed. A flag is a review prompt, not proof of measurement error or misconduct.

## Interpretation limits

These are descriptive statistics only. The module does not perform hypothesis tests, estimate statistical significance, calculate confidence intervals, fit causal or predictive models, establish measurement validity, or certify independent replication. The output values' units, measurement procedures, uncertainty and experimental comparability must be reviewed in context. One observation is explicitly classified as a single observation; its sample standard deviation is null.

The endpoint does not write to the research store, create tasks, schedule work or execute simulations or physical experiments. Scientific interpretation and any consequential decision remain subject to qualified human review.

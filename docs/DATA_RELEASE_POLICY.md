# Data Release Policy

The original study uses authorized internal platform logs from a deployed
mobile news application. The raw and row-level processed data are not suitable
for public release because timestamped user traces can create re-identification
risk even after direct identifiers are removed.

## Non-public Artifacts

- raw exports from production systems,
- timestamped click logs,
- recommendation user-day item lists,
- user profile rows,
- row-level joined article-click records,
- user-level model feature tables,
- any file containing real production user identifiers, email, device
  identifiers, account identifiers, or session-level traces. Synthetic schema
  examples may use placeholder column names such as `user_id` when the values
  are toy identifiers rather than production identifiers.

## Release-safe Artifacts

- aggregate tables without user identifiers,
- figure images generated from aggregates,
- metric and modeling code,
- synthetic table schemas,
- documentation of preprocessing decisions,
- paper PDFs and Markdown drafts after blind-review checks.

## Why Aggregates Are Used

The paper's contribution is a measurement framework and bounded empirical
audit, not a public benchmark dataset. Aggregate release preserves the
scientific claims while avoiding redistribution of private behavioral traces.

## Recommended Public Statement

Raw operational logs cannot be released because they contain timestamped
platform behavior traces. The public release package provides executable metric
code, aggregate outputs used in the paper, figure-generation scripts,
release-safe notebooks, and synthetic schemas documenting the table structure.
Authorized private reruns additionally use output-stripped notebooks and
approved processed logs outside the public repository.

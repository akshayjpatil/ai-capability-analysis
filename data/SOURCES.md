# Data source log

Before analyzing a source, record its exact URL, upstream commit or release, download date, license, columns, unit of observation, and transformations here. Keep release dates distinct from the date a model was evaluated or a leaderboard snapshot was taken.

| Source | Official entry point | Proposed local input | Unit and caution |
| --- | --- | --- | --- |
| METR | https://github.com/METR/eval-analysis-public | `data/processed/metr_horizons.csv` | One agent fit per evaluation methodology; time horizon estimates are not independent task observations. Do not silently mix v1.0 and v1.1. |
| LiveBench | https://github.com/LiveBench/LiveBench | `data/processed/livebench_scores.csv` | One model × category × benchmark release; pin the release and aggregation rules. |
| SWE-bench | https://github.com/SWE-bench/swe-bench.github.io | `data/processed/swebench_verified.csv` | One Verified submission; dates are submission/evaluation dates, not necessarily model release dates. |

## Proposed normalized schemas

These files do **not** exist in the starter. Create them only after examining the actual upstream fields and documenting the mapping.

- `metr_horizons.csv`: `model,release_date,eval_date,methodology,p50_minutes`
- `livebench_scores.csv`: `model,release_date,snapshot_date,benchmark_release,category,score`
- `swebench_verified.csv`: `system,submission_date,benchmark_version,resolved_pct`

Use ISO `YYYY-MM-DD` dates and numeric metrics. Document whether a score is 0–1 or 0–100. The notebook currently plots only a provided, normalized METR table; the other sections define the next analysis steps.

## Snapshot record template

```text
Source:
Exact URL/path:
Retrieved (UTC):
Upstream commit/release:
License / redistribution notes:
Rows and unit of observation:
Original columns:
Filtering and deduplication:
Model alias mapping:
Missing values / exclusions:
```

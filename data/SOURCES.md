# Data source log

Running the notebook calls `src.data_sources.fetch_all`. It downloads source snapshots over HTTPS and records URLs, hashes, timestamp, and GitHub revisions in the ignored local `data/raw/manifest.json`. Review licenses and redistribution conditions separately. Keep release dates distinct from the date a model was evaluated, a benchmark was released, or a leaderboard submission occurred.

| Source | Official entry point | Proposed local input | Unit and caution |
| --- | --- | --- | --- |
| METR | https://metr.org/assets/benchmark_results_1_1.yaml | `data/processed/metr_horizons.csv` | One model/agent fit for Time Horizon 1.1. The website asset is mutable; SHA-256 is recorded. `eval_date` is missing, not inferred. |
| LiveBench | https://github.com/LiveBench/new-livebench/tree/main/public | `data/processed/livebench_scores.csv` | One model × category × benchmark release. Category score is the unweighted mean of available subtask scores, with coverage columns. No model release date is inferred from its name. |
| SWE-bench | https://github.com/SWE-bench/swe-bench.github.io/blob/master/data/leaderboards.json | `data/processed/swebench_verified.csv` | One Verified leaderboard submission. `submission_date` is not model release; `benchmark_version=Verified` identifies the split, not a fixed harness revision. |

## Proposed normalized schemas

The fetcher creates these normalized files. Raw files and processed extracts are ignored by Git and can be refreshed with `fetch_all(ROOT, refresh=True)`.

- `metr_horizons.csv`: `model,release_date,eval_date,methodology,p50_minutes,p50_ci_low_minutes,p50_ci_high_minutes,is_sota`
- `livebench_scores.csv`: `model,release_date,snapshot_date,benchmark_release,category,score,subtasks_scored,subtasks_total`
- `swebench_verified.csv`: `system,agent,model,submission_date,benchmark_version,resolved_pct,submission_id,warning`

Use ISO `YYYY-MM-DD` dates and numeric metrics. METR horizons are minutes; LiveBench category scores and SWE-bench resolved values are 0–100. LiveBench's `snapshot_date` in this extract is the *benchmark release date*, not a historical snapshot of user preference. Published releases jump from May 2025 to November 2025, so the project cannot claim an exact September 2025 LiveBench baseline.

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

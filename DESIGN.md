# Comparison Design — Has AI Become Dumber?

## Question

Across comparable public evaluations, did measured AI capability decline, increase, or move differently by domain, from late 2025 to mid-2026?

Product experience and user preference are separate questions that need their own evidence.

> Note: the original headline, September 2025 vs September 2026, is not supported by the data currently available. METR Time Horizon 1.1 reaches April 2026 model releases; LiveBench tables reach June 2026 and skip September 2025; SWE-bench dates denote system submissions, not model releases. This design reframes the comparison to what the data can answer.

## Ground rules — all sources

- Keep model release date, evaluation date, and leaderboard snapshot date distinct.
- Compare scores only within a stable benchmark version, task suite, methodology, and scoring rule.
- A leaderboard is a selected set of submissions, not a random sample of all models or users.
- Random sampling is for reproducible exploration within a defined sampling frame. It does not remove selection bias in that frame.
- A bootstrap interval describes sampling uncertainty under its assumptions; it does not correct benchmark drift, correlated models, or measurement bias.
- Keep METR minutes, LiveBench scores, and SWE-bench percentages separate. Never average them into one intelligence score.

## 1. METR — autonomous task horizon

- **Unit:** one model/agent fit, Time Horizon 1.1 only. Never silently merge Time Horizon 1.0 and 1.1.
- **Date field:** `release_date` only. `eval_date` is missing, not inferred.
- **Cohorts:**
  - A: models released before 2025-09-01
  - B: models released 2025-09-01 to 2026-04-30 (last available in 1.1)
- **Metric:** `p50_minutes`, log scale, median per cohort, split by `methodology`. Do not pool methodologies.
- **Statistic:** report median A, median B, median difference, and n per cohort. Do not use a bootstrap that assumes independent rows as the headline uncertainty — models from the same family are correlated.
- **Exclusions:** drop missing / `p50 <= 0`. Keep the METR-provided p50 CI as a descriptor, not as the analysis uncertainty interval.

## 2. LiveBench — benchmark performance by category

- **Unit:** one model × category × benchmark release. Category score is the unweighted mean of available subtask scores, with coverage columns.
- **Date field:** `benchmark_release` / `snapshot_date` — not model release date.
- **Cohorts — paired only:**
  - A: November 2025 release
  - B: June 2026 release
  - Published releases jump from May 2025 to November 2025, so an exact September 2025 LiveBench baseline cannot be claimed.
- **Inclusion:** only models present in *both* releases, same category, same subtask coverage. A newer test set can change difficulty; a raw change between releases is not automatically a capability change.
- **Metric:** per-category score, 0–100, reported per category. No overall mean across categories.
- **Statistic:** paired difference per model-category, median paired change, plus count improved / declined / unchanged.

## 3. SWE-bench Verified — coding systems

- **Unit:** one Verified leaderboard submission. `submission_date` is not model release; `benchmark_version=Verified` identifies the split, not a fixed harness revision.
- **Date field:** `submission_date` only.
- **Cohorts:**
  - A: submissions 2025-09-01 to 2025-12-31
  - B: submissions 2026-01-01 to 2026-09-30
- **Deduplication — pre-register one rule:** first submission per (system, model) in each window. Report sensitivity using max `resolved_pct` per system as a check; do not switch after seeing results.
- **Metric:** `resolved_pct`, median per cohort, plus n.
- **Caveat:** the evaluated system includes scaffolding and tools, and submission dates are not model release dates. Audit warnings and harness changes before inferring trends.

## Model alias mapping

Canonical family = provider + base model, no date / snapshot suffix, no agent scaffolding in the name. Keep the original name in a separate column, and log every mapping.

Example rules:

- `gpt-5-2025-08-07`, `gpt-5-chat` → `GPT-5` family, keep variant in `model_original`
- `claude-sonnet-4-20250514`, `claude-opus-4-1` → `Claude Sonnet 4` / `Claude Opus 4.1` — do not collapse Sonnet into Opus
- Same for Gemini / Grok / Llama — never infer a model release date from its name.

If two names cannot be confidently mapped, exclude that row from the paired comparison and list it in a coverage table.

## Synthesis — how to conclude

One table, one row per source:

| Source | Can answer | Cohort A → B | Metric | Finding | Limitation |
|---|---|---|---|---|---|
| METR |  |  | p50 minutes, median |  |  |
| LiveBench |  | Nov 2025 → Jun 2026 | category score, paired median change |  |  |
| SWE-bench Verified |  | Sep–Dec 2025 → Jan–Sep 2026 | resolved %, median |  |  |

Claim a decline / increase **per source only**, and only if:

1. the median paired/cohort difference is in the same direction, and
2. the result survives the sensitivity check (first vs max submission for SWE-bench, paired-only vs all-models for LiveBench).

If METR says up, LiveBench says flat, and SWE-bench says up — that is the finding. Do not force them into one verdict.

## Out of scope

Human preference and everyday reliability. That needs repeated trials on fixed tasks with stable prompts, settings, tools, and success criteria — benchmark scores alone cannot show whether an AI product feels more reliable. This section is a research gap, not a result.

## Reproducibility

Before publication, record the exact source revision and cleaning rules in `data/SOURCES.md`, with URL, retrieval date, GitHub revision where available, and SHA-256 for each source file. Do not publish a directional conclusion until comparable cohorts and missingness have been analyzed.

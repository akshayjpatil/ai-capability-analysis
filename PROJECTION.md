# Projection — Where AI Models Are Heading

Compared with the analysis in `notebooks/02_comparison_and_projection.ipynb`
and the design in `DESIGN.md`. Data retrieved 2026-11-21.

**Read this file in two parts. OBSERVED is what the public sources
actually show, with dates and n. PROJECTED is extrapolation — it
states its assumptions and why it could be wrong. Do not quote a
projected number as an observed result.**

## OBSERVED

### METR — autonomous task horizon (Time Horizon 1.1 only)

- Source: `https://metr.org/assets/benchmark_results_1_1.yaml`, retrieved 2026-11-21.
- Valid v1.1 rows: n = 23. Last model release in the file: 2026-04-07.
  No model releases after 2026-04-07 are in this file.
- Cohort A, models released before 2025-09-01: n = 14, median p50 = 20.4 minutes.
  This cohort spans 2023-03-14 to 2025-08-07, so it mixes early and
  recent models — it is not a clean September 2025 baseline.
- Cohort B, models released 2025-09-01 to 2026-04-30: n = 9,
  median p50 = 349.5 minutes, range 223.7–1044.8 minutes.
  Releases in B: 2025-11-18 to 2026-04-07.
- Sensitivity cohort, models released 2025-01-01 to 2025-08-31: n = 5,
  median p50 = 100.5 minutes. B / recent-A is about 3.5×; B / all-A
  is about 17×, and that larger ratio is confounded by the early
  2023–2024 models in A.
- METR's own doubling time, from 2023 on: 128.7 days
  (95% CI 104.4–158.0 days). All-time stitched: 187.8 days.
- Highest single p50 in B: 1044.8 minutes (~17.4 hours),
  `claude_mythos_preview_early`, released 2026-04-07. It is a preview
  model and the last point in the file — do not treat it as a typical
  model.

Finding, per source only: the frontier autonomous-task horizon rose
sharply in late 2025 to early 2026, on a small n (9 in B, 5 in the
recent-A sensitivity cohort).

### SWE-bench Verified — coding systems

- Source: SWE-bench leaderboards JSON, retrieved 2026-11-21.
  Total Verified submissions in file: n = 180, dates 2023-10-10 to 2026-02-26.
  No submissions after 2026-02-26 are in this file.
- Cohort A, submissions 2025-09-01 to 2025-12-31: raw n = 32,
  first-submission dedup n = 31, median resolved = 71.2%.
- Cohort B, submissions 2026-01-01 to 2026-09-30: raw n = 13,
  first-submission dedup n = 13, median resolved = 72.8%.
  **B is February 2026 only** — submission dates 2026-02-17, 2026-02-19
  and 2026-02-26. There are no January or March–September 2026
  submissions in the file.
- Difference: +1.6 percentage points, median to median.
  Sensitivity (max resolved per system instead of first): same medians,
  71.2% and 72.8%.
- Top first-dedup submission: A 79.2%, B 76.8%.

Finding, per source only: essentially flat. The median rose slightly
while the top fell slightly, on a small, February-clustered B cohort.
This is a plateau, not a decline or a surge.

### LiveBench v1 — benchmark performance by category

- **Not verifiable from the original source on 2026-11-21.**
  - `github.com/LiveBench/new-livebench` returned 404.
  - `livebench.ai/table_2025_11_25.csv` returned 503.
  - `livebench.ai/table_2026_06_25.csv` and
    `livebench.ai/categories_2026_06_25.json` returned 404 / 503.
  - No paired Nov 2025 vs Jun 2026 numbers are reported here,
    because they could not be fetched from the source the design
    specifies. Do not use the paired function in
    `src/comparison.py` as evidence until the tables are fetchable again.
- LiveBench 2.0 is a **different benchmark, not a continuation of v1**.
  It was first released 2026-10-14, with seven suites and different
  tasks and scoring, so 2.0 scores are not comparable with v1 scores.
- LiveBench 2.0 snapshot, `livebench.ai/data/20261025/table.csv`,
  release 2026-10-25, retrieved 2026-11-21: n = 32 models.
  - Weighted overall (long-agentic ×2, coding ×1.5, design ×1.5):
    median 65.7, top Claude Fable 5.1 at 85.7, GPT-6 Astra at 85.6,
    Claude Opus 5.5 at 85.1.
  - Per-suite medians: long-agentic 29.4, reasoning 86.7, coding 85.1,
    browser 59.9, data analysis 76.6, research 77.3, design 77.1.
  - Long-agentic is the lowest and widest-spread suite
    (range 7.3–77.9); reasoning and coding are already high and narrow.

Finding, per source only: no v1 paired finding can be claimed today.
The 2.0 snapshot shows frontier models are strong on short
reasoning / coding and much weaker, and much more spread out, on
long-horizon agentic work.

## PROJECTED

Assumptions for all projections below: the observed trend continues
at roughly its observed rate, the benchmark methodology stays stable,
and no new benchmark replaces the one being projected. If any of
those break, the projection breaks with them.

### METR horizon — if the doubling rate holds

Start from the observed B median, 349.5 minutes, centred on
early 2026, and apply METR's from-2023 doubling time of ~129 days:

| Approx. date | Projected median p50 | What it means |
|---|---|---|
| Aug 2026 | ~700 minutes (~12 h) | A frontier model completes half of tasks up to ~12 h long |
| Dec 2026 – Jan 2027 | ~1,400 minutes (~23 h) | Half of tasks up to about a day long |
| Apr – May 2027 | ~2,800 minutes (~47 h) | Half of tasks up to about two days long |

Why this could be wrong, in order of importance:

1. **Saturation / harder tasks.** METR can add harder tasks, and
   frontier models can hit reliability, memory, or cost limits that
   a simple doubling curve ignores.
2. **Small n and a preview outlier.** B is n = 9, and its highest
   point (1044.8 minutes) is a preview model. The median is less
   sensitive to that point than the mean, but the cohort is still small.
3. **Stale source.** The YAML retrieved 2026-11-21 ends at
   2026-04-07. If METR has not published newer results, or has
   changed methodology, the extrapolation has no new anchor.
4. **Horizon is not reliability.** p50 is the task length at 50%
   success. A longer horizon does not mean a product is reliable,
   cheap, or safe to deploy unattended.

### SWE-bench Verified — plateau, then replacement

Projected: median resolved stays in the low-to-mid 70s for the next
two cohorts, gaining roughly 0–3 percentage points per six months,
with the top staying near 80%.

Why: the observed move was +1.6 points on a February-clustered
n = 13, the top fell, and Verified is a fixed task set. Fixed
benchmarks saturate. The next gains are more likely to show up as
new, harder coding benchmarks, better agentic scaffolding around
the same models, or higher scores on long-horizon coding tasks —
not as a large jump in Verified resolved %.

Why this could be wrong: a new model generation or a new agent
scaffold could jump the median by 5+ points in one release, or
the leaderboard could stop being updated (as the file already
shows no submissions after 2026-02-26).

### LiveBench — the shift is to long-horizon agentic work

Projected: the fastest frontier gains over the next year will be
in long-agentic, browser, and research work — the suites where
the 2.0 median is lowest (long-agentic 29.4, browser 59.9) —
while reasoning (86.7) and coding (85.1) gain slowly, because
they are already near the top of a 0–100 scale.

Why: that is where the headroom is, and it is also where the
benchmark itself moved — LiveBench 2.0 replaced short questions
with long-running work: extending applications over changing
requirements, fixing bugs in real merged PRs, working in a real
browser, and writing research reports.

Why this could be wrong: long-agentic scores depend heavily on
scaffolding, tools, cost limits, and effort settings, not just
the model. A change in any of those can move scores without a
change in underlying capability, and 2.0 has only one observed
release in this analysis, so there is no 2.0 trend yet — only a
single snapshot.

## Headline

Autonomous-task horizons are still doubling roughly every four
months on the observed frontier, coding on SWE-bench Verified has
plateaued in the low 70s, and evaluation itself is shifting to
long-horizon agentic work where the median model still scores
only about 29/100. The next year is likely to be won or lost on
orchestration, memory, and failure recovery over hours-long tasks —
not on short benchmark questions.

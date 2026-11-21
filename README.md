# Has AI Become Dumber?

A reproducible notebook project asking how publicly reported AI capability changed from late 2025 to mid-2026. The analysis compares separate measures of autonomous task completion, benchmark performance, and software engineering performance. It will not assume that a higher benchmark score implies a better everyday product experience.

> Reframed question: the original September 2025 vs September 2026 headline is not supported by the data — METR Time Horizon 1.1 reaches April 2026 model releases, LiveBench v1 reaches June 2026 and skips September 2025, and SWE-bench dates are submissions, not model releases. See `DESIGN.md` and `notebooks/02_comparison_and_projection.ipynb`.

## Status

**Comparison implemented.** The comparison design is in `DESIGN.md`, implemented in `src/comparison.py`, and run in `notebooks/02_comparison_and_projection.ipynb`. The projection is in `PROJECTION.md`. Running notebook 01 still fetches public source files and caches them locally. LiveBench v1 tables were not fetchable from their original source on 2026-11-21 (see notebook 02), so no paired LiveBench v1 finding is claimed.

## Get started

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

Open `notebooks/01_ai_capability_analysis.ipynb` and run all cells. The first run fetches METR's public YAML, all paired LiveBench release CSV/JSON files, and SWE-bench's leaderboard JSON through public HTTPS endpoints; no key is required. It stores the responses under `data/raw/`, normalized tables under `data/processed/`, and hashes/revisions in `data/raw/manifest.json`. Reruns use this cache. Call `fetch_all(ROOT, refresh=True)` to take a new snapshot. The initial fetch may take a couple of minutes.

The same acquisition can be run from the repository root without opening Jupyter:

```bash
python -c "from pathlib import Path; from src.data_sources import fetch_all; print(fetch_all(Path('.'))['row_counts'])"
```

## Project layout

```text
notebooks/01_ai_capability_analysis.ipynb  Research narrative and analysis
notebooks/02_comparison_and_projection.ipynb  Comparison and projection (DESIGN.md)
DESIGN.md                               Comparison design (late 2025 vs mid-2026)
PROJECTION.md                           Projection, observed vs projected
data/SOURCES.md                         Source and schema notes
data/raw/                              Downloaded source snapshots (local)
data/processed/                        Cleaned analysis tables (local)
src/data_sources.py                    Public fetch and normalization code
src/comparison.py                      Pure comparison helpers (alias mapping, cohorts, paired diff, dedup)
```

## Research design

See `DESIGN.md` for the full design. In short:

- **Question:** Do comparable public evaluations show a decline in measurable model capability from late 2025 to mid-2026? Which dimensions move differently?
- **Unit of observation:** Depends on the source: an evaluated agent, model and task run, benchmark score, or leaderboard submission. Record the unit before sampling.
- **Sampling:** Use a fixed NumPy seed for reproducible random exploration. Sample within a defined frame and period; a random sample of all published models is not representative of frontier models or user experience.
- **Comparison:** Compare like with like within a source, task suite, version, and metric. Preserve release date and evaluation or snapshot date separately. Use broad windows only when they contain adequate comparable observations. METR: Time Horizon 1.1 only, release date only, before 2025-09-01 vs 2025-09-01 to 2026-04-30. LiveBench v1: paired only, Nov 2025 vs Jun 2026. SWE-bench Verified: submission date only, Sep–Dec 2025 vs Jan–Sep 2026, first submission per (system, model).
- **Uncertainty:** Bootstrap an explicitly named statistic when independent observations support it. Repeated submissions from one model family, correlated task runs, and leaderboard selection can invalidate naive intervals.
- **Synthesis:** Report each measure separately. Do not average METR time horizons, LiveBench scores, SWE-bench resolution rates, or Arena preference ratings into one intelligence score.

The previous discussion also proposed a large model database for random sampling. That may describe the wider model population, but it cannot answer this frontier capability question unless comparable scores and a valid sampling frame exist. The starter leaves it out of the headline comparison.

## Public source candidates

| Source | What to inspect | Starting point |
| --- | --- | --- |
| METR time horizon | Published Time Horizon 1.1 YAML, including p50 estimates | [METR results page](https://metr.org/time-horizons/) |
| LiveBench | Dated release tables and category mappings, pinned to one GitHub commit | [LiveBench release format](https://github.com/LiveBench/new-livebench) |
| SWE-bench | Verified leaderboard submissions and resolved percentage, pinned to one GitHub commit | [SWE-bench leaderboard repository](https://github.com/SWE-bench/swe-bench.github.io) |

These are separate datasets, not one merged intelligence score. The published LiveBench series has no September 2025 release; its nearest dated tables are November 2025 and June 2026. METR's site asset does not provide a per-model evaluation date, while SWE-bench dates denote submissions rather than model releases. See `data/SOURCES.md` for exact fields and caveats. Human-preference data can be added once comparable historical snapshots are established.

## Reproducibility and publication

The fetcher records URL, retrieval date, GitHub revision where available, and SHA-256 for each source file. Review upstream licenses and any redistribution restrictions before republishing raw data. Raw and processed data are excluded from Git, while the acquisition code remains reproducible. Export figures after running the notebook and link the public repository from the eventual Medium article. Do not publish a directional conclusion until comparable cohorts and missingness have been analyzed.

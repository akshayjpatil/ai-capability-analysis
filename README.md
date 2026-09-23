# Has AI Become Dumber?

A reproducible notebook project asking how publicly reported AI capability changed between September 2025 and September 2026. The analysis will compare separate measures of autonomous task completion, benchmark performance, and software engineering performance. It will not assume that a higher benchmark score implies a better everyday product experience.

## Status

**Starter scaffold.** The notebook runs without downloaded data and labels missing inputs. It contains no results or conclusions yet. Source snapshots, cleaning decisions, model identity mapping, and final analysis remain to be added.

## Get started

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

Open `notebooks/01_ai_capability_analysis.ipynb` and run all cells. The notebook uses NumPy, pandas, and Matplotlib. Populate the source-specific files described in `data/SOURCES.md` to activate its analysis sections.

## Project layout

```text
notebooks/01_ai_capability_analysis.ipynb  Research narrative and analysis
data/SOURCES.md                         Source and schema notes
data/raw/                              Downloaded source snapshots (local)
data/processed/                        Cleaned analysis tables (local)
src/                                   Reserved for reusable code
```

## Research design

- **Question:** Do comparable public evaluations show a decline in measurable model capability from September 2025 to September 2026? Which dimensions move differently?
- **Unit of observation:** Depends on the source: an evaluated agent, model and task run, benchmark score, or leaderboard submission. Record the unit before sampling.
- **Sampling:** Use a fixed NumPy seed for reproducible random exploration. Sample within a defined frame and period; a random sample of all published models is not representative of frontier models or user experience.
- **Comparison:** Compare like with like within a source, task suite, version, and metric. Preserve release date and evaluation or snapshot date separately. Use broad windows only when they contain adequate comparable observations.
- **Uncertainty:** Bootstrap an explicitly named statistic when independent observations support it. Repeated submissions from one model family, correlated task runs, and leaderboard selection can invalidate naive intervals.
- **Synthesis:** Report each measure separately. Do not average METR time horizons, LiveBench scores, SWE-bench resolution rates, or Arena preference ratings into one intelligence score.

The previous discussion also proposed a large model database for random sampling. That may describe the wider model population, but it cannot answer this frontier capability question unless comparable scores and a valid sampling frame exist. The starter leaves it out of the headline comparison.

## Public source candidates

| Source | What to inspect | Starting point |
| --- | --- | --- |
| METR time horizon | Agent success by task duration and published fits | [METR analysis repository](https://github.com/METR/eval-analysis-public) |
| LiveBench | Category and task scores, with benchmark release pinned | [LiveBench repository](https://github.com/LiveBench/LiveBench) |
| SWE-bench | Verified leaderboard submissions and resolved percentage | [SWE-bench leaderboard repository](https://github.com/SWE-bench/swe-bench.github.io) |

These are source candidates, not pre-merged data. See `data/SOURCES.md` for the snapshot and schema checklist. Human-preference data can be added later once a source with usable historical snapshots and stable comparison rules is selected.

## Reproducibility and publication

Record the download URL, retrieval date, upstream revision, license, filtering rules, and any model-name joins for each snapshot. Source datasets may be large or have redistribution constraints, so raw and processed data are excluded from Git; keep a documented acquisition path. Export figures after running the notebook and link the public repository from the eventual Medium article. Do not publish a directional conclusion until the analysis has run.

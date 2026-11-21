"""Pure comparison helpers for Has AI Become Dumber?

Implements DESIGN.md. No merged intelligence score: each source is
compared separately, in its own units, with its own date field.

Functions here are pure (no network, no file I/O) so they can be
tested by hand on small tables. The notebook is responsible for
fetching data and for reporting coverage / missing data.
"""

from __future__ import annotations

import re
from datetime import date

# ---------------------------------------------------------------------------
# Model alias mapping
# ---------------------------------------------------------------------------

# Canonical family per provider. Keys are lower-cased, punctuation-free
# prefixes; values are the canonical family name. Keep this list small
# and explicit: if a model does not match, it is unmappable, not guessed.
_FAMILY_PREFIXES = (
    ("claudeopus", "Claude Opus"),
    ("claude", "Claude"),
    ("gpt", "GPT"),
    ("gemini", "Gemini"),
    ("grok", "Grok"),
    ("llama", "Llama"),
    ("qwen", "Qwen"),
    ("deepseek", "DeepSeek"),
    ("mistral", "Mistral"),
    ("gemma", "Gemma"),
)


def canonical_family(model: str) -> str | None:
    """Return a canonical provider+base-model family, or None if unmappable.

    Rules (DESIGN.md): strip date / snapshot suffixes and agent
    scaffolding from the name, keep the original name elsewhere, and
    never infer a release date from a name. Sonnet and Opus are never
    collapsed into each other, and neither are distinct GPT generations.

    Examples:
        "gpt-5-2025-08-07" -> "GPT-5"
        "gpt-5-chat" -> "GPT-5"
        "claude-sonnet-4-20250514" -> "Claude Sonnet 4"
        "claude-opus-4-1" -> "Claude Opus 4.1"
    """
    if not model or not isinstance(model, str):
        return None
    name = model.strip().lower()
    # Remove common scaffolding / effort suffixes.
    name = re.sub(r"(_inspect|_max|_high|_medium|_low|_thinking.*|_chat)$", "", name)
    name = name.replace("_", "-").replace(" ", "-")
    # Drop a trailing YYYYMMDD / YYYY-MM-DD date.
    name = re.sub(r"-\d{8}$", "", name)
    name = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", name)

    # Claude: keep the tier (sonnet / opus / haiku) and the generation.
    m = re.match(r"claude-(opus|sonnet|haiku)-(\d+(?:[.-]\d+)?)", name)
    if m:
        return f"Claude {m.group(1).title()} {m.group(2).replace('-', '.')}"
    m = re.match(r"claude-(\d+(?:[.-]\d+)?)", name)
    if m:
        return f"Claude {m.group(1).replace('-', '.')}"
    # GPT: keep the generation number (5, 5.1, 6, ...).
    m = re.match(r"gpt-(\d+(?:[.-]\d+)?)", name)
    if m:
        return f"GPT-{m.group(1).replace('-', '.')}"
    # Gemini: keep the generation number.
    m = re.match(r"gemini-(\d+(?:[.-]\d+)?)", name)
    if m:
        return f"Gemini {m.group(1).replace('-', '.')}"
    # Other providers: family only, no version guessing from free text.
    squashed = name.replace("-", "")
    for prefix, family in _FAMILY_PREFIXES:
        if squashed.startswith(prefix):
            return family
    return None


def alias_mapping(rows):
    """Map a list of ``{"model": ...}`` rows to canonical families.

    Returns ``(mapped, unmapped)`` where mapped is a list of dicts with
    ``model_original`` and ``family`` added, and unmapped is the list of
    original names that could not be confidently mapped. Unmapped rows
    are excluded from paired comparisons and must be listed in a
    coverage table (DESIGN.md).
    """
    mapped, unmapped = [], []
    for row in rows:
        family = canonical_family(row.get("model", ""))
        if family is None:
            unmapped.append(row.get("model", ""))
        else:
            mapped.append({**row, "model_original": row.get("model", ""), "family": family})
    return mapped, unmapped


# ---------------------------------------------------------------------------
# Small statistics helpers (no external dependencies)
# ---------------------------------------------------------------------------

def median(values):
    """Median of a list of numbers, or None if empty."""
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    n = len(vals)
    mid = n // 2
    if n % 2:
        return float(vals[mid])
    return float((vals[mid - 1] + vals[mid]) / 2)


def _parse_date(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# METR
# ---------------------------------------------------------------------------

def metr_cohort_split(rows, methodology="METR-Horizon-v1.1"):
    """Split METR rows into the DESIGN.md cohorts, v1.1 only.

    Rows are dicts with ``release_date`` (ISO date), ``methodology``
    and ``p50_minutes``. Drops missing / ``p50 <= 0`` rows.
    Returns a dict with n and median p50 per cohort, plus the
    sensitivity cohort (models released 2025-01-01 to 2025-08-31).
    """
    valid = []
    for row in rows:
        if row.get("methodology") != methodology:
            continue
        p50 = row.get("p50_minutes")
        released = _parse_date(row.get("release_date"))
        if p50 is None or released is None:
            continue
        try:
            p50 = float(p50)
        except (TypeError, ValueError):
            continue
        if p50 <= 0:
            continue
        valid.append({**row, "release_date": released, "p50_minutes": p50})

    cohort_a = [r for r in valid if r["release_date"] < date(2025, 9, 1)]
    cohort_b = [
        r for r in valid if date(2025, 9, 1) <= r["release_date"] <= date(2026, 4, 30)
    ]
    recent_a = [
        r for r in valid if date(2025, 1, 1) <= r["release_date"] < date(2025, 9, 1)
    ]
    return {
        "methodology": methodology,
        "n_total_valid": len(valid),
        "cohort_a_before_2025_09_01": {
            "n": len(cohort_a),
            "median_p50_minutes": median([r["p50_minutes"] for r in cohort_a]),
        },
        "cohort_b_2025_09_01_to_2026_04_30": {
            "n": len(cohort_b),
            "median_p50_minutes": median([r["p50_minutes"] for r in cohort_b]),
        },
        "sensitivity_recent_a_2025_01_01_to_2025_08_31": {
            "n": len(recent_a),
            "median_p50_minutes": median([r["p50_minutes"] for r in recent_a]),
        },
    }


# ---------------------------------------------------------------------------
# LiveBench
# ---------------------------------------------------------------------------

def livebench_paired_diff(rows_a, rows_b):
    """Paired LiveBench comparison between two benchmark releases.

    Each row is a dict with ``model``, ``category``, ``score`` (0-100)
    and ``subtasks_scored`` / ``subtasks_total``. Only models present
    in *both* releases, in the same category, with the same subtask
    coverage, are paired. Returns per-category median paired change
    and improved / declined / unchanged counts, plus the list of
    unpaired model-category pairs for the coverage table.
    """
    def keyed(rows):
        out = {}
        for row in rows:
            score = row.get("score")
            if score is None:
                continue
            out[(row.get("model"), row.get("category"))] = row
        return out

    a, b = keyed(rows_a), keyed(rows_b)
    paired, unpaired = [], []
    for key in sorted(set(a) | set(b)):
        if key not in a or key not in b:
            unpaired.append({"model": key[0], "category": key[1]})
            continue
        if (a[key].get("subtasks_scored"), a[key].get("subtasks_total")) != (
            b[key].get("subtasks_scored"),
            b[key].get("subtasks_total"),
        ):
            unpaired.append({"model": key[0], "category": key[1], "reason": "coverage changed"})
            continue
        paired.append(
            {
                "model": key[0],
                "category": key[1],
                "score_a": float(a[key]["score"]),
                "score_b": float(b[key]["score"]),
                "diff": float(b[key]["score"]) - float(a[key]["score"]),
            }
        )

    by_category = {}
    for category in sorted({p["category"] for p in paired}):
        diffs = [p["diff"] for p in paired if p["category"] == category]
        by_category[category] = {
            "n_paired": len(diffs),
            "median_paired_change": median(diffs),
            "improved": sum(1 for d in diffs if d > 0),
            "declined": sum(1 for d in diffs if d < 0),
            "unchanged": sum(1 for d in diffs if d == 0),
        }
    return {"by_category": by_category, "n_paired": len(paired), "unpaired": unpaired}


# ---------------------------------------------------------------------------
# SWE-bench Verified
# ---------------------------------------------------------------------------

def swebench_first_submission(rows):
    """First submission per (system, model) per window, as pre-registered.

    Rows are dicts with ``system``, ``model``, ``submission_date``
    (ISO date) and ``resolved_pct``. ``window`` must be ``"A"``
    (2025-09-01 to 2025-12-31) or ``"B"`` (2026-01-01 to 2026-09-30).
    Returns the deduplicated rows, sorted by submission date.
    """
    raise ValueError("use swebench_cohort(rows, window) — window is required")


def swebench_cohort(rows, window):
    """Deduplicated SWE-bench Verified cohort for one window.

    Pre-registered rule (DESIGN.md): first submission per
    (system, model) in the window. ``window`` is ``"A"``
    (2025-09-01 to 2025-12-31) or ``"B"`` (2026-01-01 to 2026-09-30).
    Returns ``{"n_raw": ..., "n_dedup": ..., "median_resolved_pct": ...,
    "rows": [...]}``.
    """
    windows = {
        "A": (date(2025, 9, 1), date(2025, 12, 31)),
        "B": (date(2026, 1, 1), date(2026, 9, 30)),
    }
    if window not in windows:
        raise ValueError(f"window must be 'A' or 'B', got {window!r}")
    start, end = windows[window]
    in_window = []
    for row in rows:
        submitted = _parse_date(row.get("submission_date"))
        resolved = row.get("resolved_pct")
        if submitted is None or resolved is None or not (start <= submitted <= end):
            continue
        try:
            resolved = float(resolved)
        except (TypeError, ValueError):
            continue
        in_window.append({**row, "submission_date": submitted, "resolved_pct": resolved})
    in_window.sort(key=lambda r: (r["submission_date"], r.get("system", ""), r.get("model", "")))
    seen, deduped = set(), []
    for row in in_window:
        key = (row.get("system"), row.get("model"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return {
        "window": window,
        "n_raw": len(in_window),
        "n_dedup": len(deduped),
        "median_resolved_pct": median([r["resolved_pct"] for r in deduped]),
        "rows": deduped,
    }


def swebench_max_sensitivity(rows, window):
    """Sensitivity check: max resolved_pct per (system, model) in a window."""
    result = swebench_cohort(rows, window)
    # Re-run the window filter, keeping the max instead of the first.
    windows = {
        "A": (date(2025, 9, 1), date(2025, 12, 31)),
        "B": (date(2026, 1, 1), date(2026, 9, 30)),
    }
    start, end = windows[window]
    best = {}
    for row in rows:
        submitted = _parse_date(row.get("submission_date"))
        resolved = row.get("resolved_pct")
        if submitted is None or resolved is None or not (start <= submitted <= end):
            continue
        key = (row.get("system"), row.get("model"))
        if key not in best or float(resolved) > best[key]["resolved_pct"]:
            best[key] = {**row, "submission_date": submitted, "resolved_pct": float(resolved)}
    kept = list(best.values())
    return {
        "window": window,
        "n_dedup": len(kept),
        "median_resolved_pct": median([r["resolved_pct"] for r in kept]),
        "first_submission_median": result["median_resolved_pct"],
    }


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------

def coverage_table(entries):
    """Build a coverage table from ``[{"source": ..., "first": ...,
    "last": ..., "rows": ...}]`` entries, sorted by source name."""
    return sorted(
        [
            {
                "source": e["source"],
                "first": str(e.get("first")),
                "last": str(e.get("last")),
                "rows": int(e.get("rows", 0)),
            }
            for e in entries
        ],
        key=lambda e: e["source"],
    )

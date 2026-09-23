"""Fetch public source snapshots and build source-specific analysis tables."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd
import yaml


USER_AGENT = "ai-capability-analysis/0.1 (public research notebook)"
METR_URL = "https://metr.org/assets/benchmark_results_1_1.yaml"
GITHUB_API = "https://api.github.com/repos"
GITHUB_RAW = "https://raw.githubusercontent.com"


def _get(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=90) as response:
        return response.read()


def _json(url: str) -> dict | list:
    return json.loads(_get(url))


def _revision(owner: str, repo: str, branch: str) -> str:
    return _json(f"{GITHUB_API}/{owner}/{repo}/commits/{branch}")["sha"]


def _snapshot(url: str, path: Path, records: list[dict], refresh: bool) -> bytes:
    if refresh or not path.exists():
        content = _get(url)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    else:
        content = path.read_bytes()
    records.append({
        "url": url,
        "path": str(path),
        "sha256": hashlib.sha256(content).hexdigest(),
        "bytes": len(content),
    })
    return content


def _metr(root: Path, records: list[dict], refresh: bool) -> pd.DataFrame:
    raw = _snapshot(METR_URL, root / "data/raw/metr/benchmark_results_1_1.yaml", records, refresh)
    document = yaml.safe_load(raw)
    rows = []
    for model, item in document["results"].items():
        p50 = item.get("metrics", {}).get("p50_horizon_length", {})
        rows.append({
            "model": model,
            "release_date": item.get("release_date"),
            "eval_date": None,  # Not supplied per model by this asset.
            "methodology": item.get("benchmark_name", document["benchmark_name"]),
            "p50_minutes": p50.get("estimate"),
            "p50_ci_low_minutes": p50.get("ci_low"),
            "p50_ci_high_minutes": p50.get("ci_high"),
            "is_sota": item.get("metrics", {}).get("is_sota"),
        })
    return pd.DataFrame(rows)


def _livebench(root: Path, records: list[dict], refresh: bool) -> tuple[pd.DataFrame, str]:
    owner, repo = "LiveBench", "new-livebench"
    revision = _revision(owner, repo, "main")
    entries = _json(f"{GITHUB_API}/{owner}/{repo}/contents/public?ref={revision}")
    names = {entry["name"] for entry in entries}
    releases = sorted(re.match(r"table_(\d{4}_\d{2}_\d{2})\.csv$", name).group(1)
                      for name in names if re.match(r"table_(\d{4}_\d{2}_\d{2})\.csv$", name))
    rows = []
    for release in releases:
        category_file = f"categories_{release}.json"
        if category_file not in names:
            raise ValueError(f"LiveBench release {release} lacks {category_file}")
        base = f"{GITHUB_RAW}/{owner}/{repo}/{revision}/public"
        table_bytes = _snapshot(f"{base}/table_{release}.csv",
                                root / f"data/raw/livebench/table_{release}.csv", records, refresh)
        categories_bytes = _snapshot(f"{base}/{category_file}",
                                     root / f"data/raw/livebench/{category_file}", records, refresh)
        table = pd.read_csv(StringIO(table_bytes.decode("utf-8")))
        categories = json.loads(categories_bytes)
        release_date = release.replace("_", "-")
        for category, subtasks in categories.items():
            absent = set(subtasks) - set(table.columns)
            if absent:
                raise ValueError(f"LiveBench {release} {category} missing columns: {sorted(absent)}")
            for _, item in table.iterrows():
                values = pd.to_numeric(item[subtasks], errors="coerce")
                rows.append({
                    "model": item["model"],
                    "release_date": None,  # Benchmark release is not model release.
                    "snapshot_date": release_date,
                    "benchmark_release": release_date,
                    "category": category,
                    "score": values.mean(),
                    "subtasks_scored": values.notna().sum(),
                    "subtasks_total": len(subtasks),
                })
    if not rows:
        raise ValueError("No LiveBench release tables found")
    return pd.DataFrame(rows), revision


def _swebench(root: Path, records: list[dict], refresh: bool) -> tuple[pd.DataFrame, str]:
    owner, repo = "SWE-bench", "swe-bench.github.io"
    revision = _revision(owner, repo, "master")
    url = f"{GITHUB_RAW}/{owner}/{repo}/{revision}/data/leaderboards.json"
    raw = _snapshot(url, root / "data/raw/swebench/leaderboards.json", records, refresh)
    boards = json.loads(raw)["leaderboards"]
    verified = next(board["results"] for board in boards if board["name"] == "Verified")
    rows = []
    for item in verified:
        rows.append({
            "system": item.get("name"),
            "agent": item.get("agent"),
            "model": item.get("model_display"),
            "submission_date": item.get("date"),
            "benchmark_version": "Verified",  # Leaderboard split, not a fixed harness revision.
            "resolved_pct": pd.to_numeric(item.get("resolved"), errors="coerce"),
            "submission_id": item.get("folder"),
            "warning": item.get("warning"),
        })
    return pd.DataFrame(rows), revision


def fetch_all(root: Path, refresh: bool = False) -> dict:
    """Download/cache source files and produce normalized CSVs plus a provenance manifest.

    `refresh=True` obtains new upstream GitHub revisions and replaces local snapshots.
    Default reruns use cached extracts if the provenance manifest already exists.
    """
    root = Path(root).resolve()
    processed = root / "data/processed"
    manifest_path = root / "data/raw/manifest.json"
    if not refresh and manifest_path.exists() and all(
        (processed / name).exists() for name in
        ("metr_horizons.csv", "livebench_scores.csv", "swebench_verified.csv")
    ):
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    # A partially completed fetch must never mix old cached files with new
    # GitHub commit URLs and then claim they belong to the newer revision.
    # Invalidate the old manifest before a requested refresh as well.
    if refresh and manifest_path.exists():
        manifest_path.unlink()
    refresh = True
    records: list[dict] = []
    metr = _metr(root, records, refresh)
    livebench, livebench_sha = _livebench(root, records, refresh)
    swebench, swebench_sha = _swebench(root, records, refresh)
    processed.mkdir(parents=True, exist_ok=True)
    for frame, name in (
        (metr, "metr_horizons.csv"),
        (livebench, "livebench_scores.csv"),
        (swebench, "swebench_verified.csv"),
    ):
        frame.to_csv(processed / name, index=False)
    manifest = {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "upstream_revisions": {
            "metr": "unversioned website asset; see SHA-256 below",
            "livebench": livebench_sha,
            "swebench": swebench_sha,
        },
        "row_counts": {"metr": len(metr), "livebench": len(livebench), "swebench": len(swebench)},
        "sources": records,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

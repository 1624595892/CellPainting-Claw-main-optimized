"""Run the demo profiling analysis pipeline with CellProfiler (optimized v4.2.8)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the demo profiling analysis pipeline with CellProfiler.",
    )
    parser.add_argument("--config", required=True, help="Path to pipeline_config.json.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config).expanduser().resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    backend_root = config_path.parent.parent
    repo_root = _find_repo_root(config_path)
    paths = payload["paths"]

    pipeline_path = _resolve_backend_path(backend_root, paths["cellprofiler_pipeline_analysis"])
    output_dir = _resolve_backend_path(backend_root, paths["cellprofiler_output_dir"])
    load_data_csv = _resolve_backend_path(backend_root, paths["load_data_with_illum_csv"])

    if not load_data_csv.exists():
        raise FileNotFoundError(f"Load-data CSV not found: {load_data_csv}")
    if not pipeline_path.exists():
        raise FileNotFoundError(f"Profiling pipeline not found: {pipeline_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Build absolute-path load_data CSV
    absolute_load_data_path = output_dir / "load_data_with_illum.absolute.csv"
    _absolutize_load_data(load_data_csv, absolute_load_data_path, repo_root=repo_root)

    cellprofiler_executable = _resolve_cellprofiler_executable()
    command = [
        str(cellprofiler_executable),
        "-c",
        "-r",
        "-p", str(pipeline_path),
        "-o", str(output_dir),
        "-i", str(repo_root),
        "--data-file", str(absolute_load_data_path),
    ]
    print("[profiling_demo] running:", " ".join(command))
    result = subprocess.run(command, check=False)
    return int(result.returncode)


def _absolutize_load_data(source_path: Path, destination_path: Path, *, repo_root: Path) -> None:
    """Convert relative load_data paths to absolute paths."""
    import pandas as pd
    df = pd.read_csv(source_path)
    for column in df.columns:
        if column.startswith("PathName_"):
            df[column] = df[column].map(
                lambda value: str(_resolve_repo_relative_path(repo_root, value))
            )
    df.to_csv(destination_path, index=False)


def _resolve_cellprofiler_executable() -> Path:
    sibling = Path(sys.executable).resolve().with_name("cellprofiler")
    if sibling.exists():
        return sibling
    resolved = shutil.which("cellprofiler")
    if resolved is None:
        raise FileNotFoundError(
            "Could not find CellProfiler executable in the current runtime."
        )
    return Path(resolved).resolve()


def _find_repo_root(config_path: Path) -> Path:
    for candidate in [config_path, *config_path.parents]:
        if (candidate / "src" / "cellpaint_pipeline").exists():
            return candidate
    raise FileNotFoundError(f"Could not determine repository root from {config_path}")


def _resolve_backend_path(backend_root: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (backend_root / candidate).resolve()


def _resolve_repo_relative_path(repo_root: Path, value: str) -> Path:
    candidate = Path(str(value)).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (repo_root / candidate).resolve()


if __name__ == "__main__":
    raise SystemExit(main())

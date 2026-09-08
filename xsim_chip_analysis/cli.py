"""Command-line entry point for xsim-chip defect inspection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import tifffile

from .inspection import analyze_against_reference


def _load_volume(path: Path) -> np.ndarray:
    suffix = path.suffix.lower()
    if suffix == ".npy":
        return np.load(path, allow_pickle=False)
    if suffix in {".tif", ".tiff"}:
        return tifffile.imread(path)
    raise ValueError(f"unsupported volume format: {path.suffix}; use .npy, .tif, or .tiff")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare a labelled 3D CT volume against an xsim-chip reference."
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path, default=Path("inspection_report.json"))
    parser.add_argument("--voxel-size-um", type=float, default=4.0)
    parser.add_argument("--min-component-voxels", type=int, default=8)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = analyze_against_reference(
        _load_volume(args.reference),
        _load_volume(args.candidate),
        voxel_size_um=args.voxel_size_um,
        min_component_voxels=args.min_component_voxels,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()


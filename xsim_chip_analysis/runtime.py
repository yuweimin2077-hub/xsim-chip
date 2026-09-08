"""Runtime profiles and memory estimates for Colab-friendly XCT experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib import metadata
import os
import platform
import subprocess
from typing import Any, Iterable

import numpy as np


@dataclass(frozen=True)
class SimulationConfig:
    """Serializable geometry and acquisition parameters for an XCT run."""

    profile: str
    volume_shape_zyx: tuple[int, int, int]
    detector_shape_rc: tuple[int, int]
    projections: int
    voxel_size_um: float
    seed: int

    def __post_init__(self) -> None:
        dimensions = (*self.volume_shape_zyx, *self.detector_shape_rc)
        if any(not isinstance(value, int) or value < 1 for value in dimensions):
            raise ValueError("volume and detector dimensions must be positive integers")
        if not isinstance(self.projections, int) or self.projections < 1:
            raise ValueError("projections must be a positive integer")
        if not np.isfinite(self.voxel_size_um) or self.voxel_size_um <= 0:
            raise ValueError("voxel_size_um must be a positive finite number")

    @classmethod
    def quick_colab(cls, seed: int = 2060) -> "SimulationConfig":
        """Small profile intended for a Colab GPU smoke test."""

        return cls(
            profile="quick-colab",
            volume_shape_zyx=(129, 129, 129),
            detector_shape_rc=(129, 192),
            projections=180,
            voxel_size_um=16.0,
            seed=seed,
        )

    @classmethod
    def nist_reference(cls) -> "SimulationConfig":
        """Published NIST dimensions used by the upstream parallel workflow."""

        return cls(
            profile="nist-reference",
            volume_shape_zyx=(751, 751, 751),
            detector_shape_rc=(1001, 1201),
            projections=2400,
            voxel_size_um=4.0,
            seed=2060,
        )


def estimate_memory(config: SimulationConfig) -> dict[str, float]:
    """Estimate major NumPy buffers used by the upstream-style workflow.

    Values are binary GiB. The estimate is deliberately transparent rather
    than presented as an exact peak: ASTRA/gVXR internal allocations and mesh
    storage are not included.
    """

    volume_voxels = int(np.prod(config.volume_shape_zyx, dtype=np.int64))
    projection_pixels = (
        config.projections
        * config.detector_shape_rc[0]
        * config.detector_shape_rc[1]
    )
    gib = float(1024**3)
    buffers = {
        "label_volume_uint8_gib": volume_voxels / gib,
        "working_volume_float32_gib": volume_voxels * 4 / gib,
        "projection_stack_float32_gib": projection_pixels * 4 / gib,
        "projection_stack_uint16_gib": projection_pixels * 2 / gib,
        "reconstruction_float32_gib": volume_voxels * 4 / gib,
    }
    buffers["declared_numpy_buffers_gib"] = sum(buffers.values())
    buffers["streamed_projection_floor_gib"] = (
        buffers["label_volume_uint8_gib"]
        + buffers["working_volume_float32_gib"]
        + buffers["projection_stack_uint16_gib"]
        + buffers["reconstruction_float32_gib"]
    )
    return {key: round(value, 4) for key, value in buffers.items()}


def _package_versions(names: Iterable[str]) -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in names:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def _gpu_snapshot() -> dict[str, str | None]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return {"available": "false", "description": None}
    description = result.stdout.strip() or None
    return {"available": str(bool(description)).lower(), "description": description}


def build_run_manifest(
    config: SimulationConfig,
    *,
    elapsed_seconds: float | None = None,
    packages: Iterable[str] = ("numpy", "scipy", "astra-toolbox", "gvxr"),
) -> dict[str, Any]:
    """Capture configuration and environment metadata for reproducibility."""

    return {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config": asdict(config),
        "memory_estimate": estimate_memory(config),
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "is_google_colab": "COLAB_RELEASE_TAG" in os.environ,
            "colab_release_tag": os.environ.get("COLAB_RELEASE_TAG"),
            "gpu": _gpu_snapshot(),
            "elapsed_seconds": elapsed_seconds,
        },
        "packages": _package_versions(packages),
    }


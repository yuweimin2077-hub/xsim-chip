"""Validated configuration and metrics for reduced polychromatic simulations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class SpectrumConfig:
    """X-ray tube spectrum settings used by the Colab gVXR experiment."""

    tube_voltage_kv: float = 160.0
    energy_bin_size_kev: float = 4.0
    exposure_mas: float = 1.0
    filters_mm: tuple[tuple[str, float], ...] = (("Al", 0.5), ("Cu", 1.0))

    def __post_init__(self) -> None:
        positive = (self.tube_voltage_kv, self.energy_bin_size_kev, self.exposure_mas)
        if any(not np.isfinite(value) or value <= 0 for value in positive):
            raise ValueError("voltage, energy-bin size, and exposure must be positive")
        if self.energy_bin_size_kev >= self.tube_voltage_kv:
            raise ValueError("energy-bin size must be smaller than tube voltage")
        for element, thickness_mm in self.filters_mm:
            if not element or not isinstance(element, str):
                raise ValueError("filter elements must be non-empty strings")
            if not np.isfinite(thickness_mm) or thickness_mm <= 0:
                raise ValueError("filter thicknesses must be positive")

    def to_manifest(self) -> dict[str, Any]:
        """Return JSON-compatible acquisition settings."""

        result = asdict(self)
        result["filters_mm"] = [
            {"element": element, "thickness_mm": thickness}
            for element, thickness in self.filters_mm
        ]
        return result


@dataclass(frozen=True)
class ConeBeamConfig:
    """Compact cone-beam geometry that fits the package in a Colab detector."""

    source_position_mm: tuple[float, float, float] = (-200.0, 0.0, 0.0)
    detector_position_mm: tuple[float, float, float] = (400.0, 0.0, 0.0)
    detector_pixels_xy: tuple[int, int] = (192, 128)
    detector_pixel_size_mm: tuple[float, float] = (0.16, 0.16)

    def __post_init__(self) -> None:
        if any(not isinstance(value, int) or value < 1 for value in self.detector_pixels_xy):
            raise ValueError("detector dimensions must be positive integers")
        numeric = (*self.source_position_mm, *self.detector_position_mm, *self.detector_pixel_size_mm)
        if any(not np.isfinite(value) for value in numeric):
            raise ValueError("cone-beam geometry values must be finite")
        if any(value <= 0 for value in self.detector_pixel_size_mm):
            raise ValueError("detector pixel sizes must be positive")
        source_x = self.source_position_mm[0]
        detector_x = self.detector_position_mm[0]
        if not source_x < 0 < detector_x:
            raise ValueError("source and detector must bracket the object plane at x=0")

    @property
    def magnification(self) -> float:
        source_x = self.source_position_mm[0]
        detector_x = self.detector_position_mm[0]
        return (detector_x - source_x) / abs(source_x)

    @property
    def object_pixel_size_mm(self) -> tuple[float, float]:
        return tuple(value / self.magnification for value in self.detector_pixel_size_mm)

    def to_manifest(self) -> dict[str, Any]:
        result = asdict(self)
        result["magnification"] = self.magnification
        result["object_pixel_size_mm"] = self.object_pixel_size_mm
        return result


def summarise_spectrum(
    energy_kev: np.ndarray, photon_counts: np.ndarray
) -> dict[str, float | int]:
    """Summarise an energy spectrum without depending on the gVXR runtime."""

    energy = np.asarray(energy_kev, dtype=np.float64)
    counts = np.asarray(photon_counts, dtype=np.float64)
    if energy.ndim != 1 or counts.ndim != 1 or energy.size != counts.size or not energy.size:
        raise ValueError("energy and photon counts must be non-empty, equally sized 1D arrays")
    if not np.all(np.isfinite(energy)) or np.any(energy <= 0):
        raise ValueError("energies must be positive and finite")
    if not np.all(np.isfinite(counts)) or np.any(counts < 0) or counts.sum() <= 0:
        raise ValueError("photon counts must be finite, non-negative, and have positive sum")

    weights = counts / counts.sum()
    return {
        "bins": int(energy.size),
        "min_energy_kev": float(energy.min()),
        "max_energy_kev": float(energy.max()),
        "mean_energy_kev": float(np.sum(energy * weights)),
        "peak_energy_kev": float(energy[int(np.argmax(counts))]),
        "fraction_below_40_kev": float(weights[energy < 40.0].sum()),
    }


def normalise_energy_image(image: np.ndarray, incident_energy: float) -> np.ndarray:
    """Convert a gVXR energy image into an ideal flat-field transmission image."""

    array = np.asarray(image, dtype=np.float32)
    if array.ndim != 2 or not np.all(np.isfinite(array)) or np.any(array < 0):
        raise ValueError("image must be a finite, non-negative 2D array")
    if not np.isfinite(incident_energy) or incident_energy <= 0:
        raise ValueError("incident energy must be positive and finite")
    return np.clip(array / float(incident_energy), 0.0, 1.0).astype(np.float32)

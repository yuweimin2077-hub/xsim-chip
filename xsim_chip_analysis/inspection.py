"""Reference-based inspection of labelled semiconductor-package volumes.

The original xsim-chip phantom uses four uint8 intensities: vacuum (0),
silicon dioxide (85), copper (170), and SAC305 solder (255).  This module
compares a candidate volume with a reference, groups differences into 3D
connected components, and reports physically scaled measurements plus
process hypotheses.  Hypotheses are screening aids, not causal proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import IntEnum
from typing import Any

import numpy as np
from scipy import ndimage


class Material(IntEnum):
    """Material labels used by the NIST xsim-chip phantom."""

    VACUUM = 0
    SILICON_DIOXIDE = 85
    COPPER = 170
    SAC305_SOLDER = 255


_DEFECT_KINDS = {
    (Material.SILICON_DIOXIDE, "missing"): "dielectric_void_or_crack",
    (Material.SILICON_DIOXIDE, "excess"): "dielectric_misalignment",
    (Material.COPPER, "missing"): "copper_open_or_underfill",
    (Material.COPPER, "excess"): "copper_bridge_or_residue",
    (Material.SAC305_SOLDER, "missing"): "solder_void_or_open",
    (Material.SAC305_SOLDER, "excess"): "solder_bridge",
}

_ROOT_CAUSES = {
    "dielectric_void_or_crack": [
        "dielectric cure or lamination non-uniformity",
        "thermomechanical stress cracking",
        "segmentation or reconstruction artefact",
    ],
    "dielectric_misalignment": [
        "layer registration error",
        "dielectric thickness variation",
        "segmentation or reconstruction artefact",
    ],
    "copper_open_or_underfill": [
        "incomplete plating or etch over-removal",
        "via or trace misregistration",
        "beam-hardening or thresholding artefact",
    ],
    "copper_bridge_or_residue": [
        "etch residue or over-plating",
        "pattern registration error",
        "partial-volume or thresholding artefact",
    ],
    "solder_void_or_open": [
        "trapped flux or outgassing during reflow",
        "insufficient solder volume or poor wetting",
        "reconstruction artefact near a high-attenuation interface",
    ],
    "solder_bridge": [
        "excess paste deposition",
        "component placement offset or solder collapse",
        "segmentation blooming around solder",
    ],
}


@dataclass(frozen=True)
class ComponentMeasurement:
    defect_id: str
    defect_kind: str
    material: str
    difference: str
    voxel_count: int
    volume_um3: float
    centroid_zyx_voxels: tuple[float, float, float]
    centroid_zyx_um: tuple[float, float, float]
    bounding_box_zyx: tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
    severity: str
    candidate_root_causes: tuple[str, ...]


def _validate(reference: np.ndarray, candidate: np.ndarray, voxel_size_um: float) -> None:
    if reference.ndim != 3 or candidate.ndim != 3:
        raise ValueError("reference and candidate must both be 3D arrays (z, y, x)")
    if reference.shape != candidate.shape:
        raise ValueError(
            f"reference and candidate shapes differ: {reference.shape} != {candidate.shape}"
        )
    if not np.isfinite(voxel_size_um) or voxel_size_um <= 0:
        raise ValueError("voxel_size_um must be a positive finite number")
    allowed = np.array([item.value for item in Material], dtype=np.int64)
    observed = np.union1d(np.unique(reference), np.unique(candidate))
    invalid = observed[~np.isin(observed, allowed)]
    if invalid.size:
        raise ValueError(f"unknown material labels: {invalid.tolist()}")


def _severity(component_fraction: float, voxel_count: int) -> str:
    if component_fraction >= 0.01 or voxel_count >= 10_000:
        return "critical"
    if component_fraction >= 0.001 or voxel_count >= 1_000:
        return "major"
    return "minor"


def _components(
    mask: np.ndarray,
    *,
    material: Material,
    difference: str,
    material_voxels: int,
    voxel_size_um: float,
    min_component_voxels: int,
) -> list[ComponentMeasurement]:
    structure = ndimage.generate_binary_structure(rank=3, connectivity=3)
    labels, count = ndimage.label(mask, structure=structure)
    objects = ndimage.find_objects(labels)
    kind = _DEFECT_KINDS[(material, difference)]
    found: list[ComponentMeasurement] = []

    for component_label in range(1, count + 1):
        positions = np.argwhere(labels == component_label)
        voxel_count = int(positions.shape[0])
        if voxel_count < min_component_voxels:
            continue
        centroid = tuple(float(value) for value in positions.mean(axis=0))
        bounds_slice = objects[component_label - 1]
        assert bounds_slice is not None
        bounds = tuple((int(axis.start), int(axis.stop)) for axis in bounds_slice)
        component_fraction = voxel_count / max(material_voxels, 1)
        found.append(
            ComponentMeasurement(
                defect_id="",  # assigned after global severity sorting
                defect_kind=kind,
                material=material.name.lower(),
                difference=difference,
                voxel_count=voxel_count,
                volume_um3=float(voxel_count * voxel_size_um**3),
                centroid_zyx_voxels=centroid,
                centroid_zyx_um=tuple(value * voxel_size_um for value in centroid),
                bounding_box_zyx=bounds,  # type: ignore[arg-type]
                severity=_severity(component_fraction, voxel_count),
                candidate_root_causes=tuple(_ROOT_CAUSES[kind]),
            )
        )
    return found


def analyze_against_reference(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    voxel_size_um: float = 4.0,
    min_component_voxels: int = 8,
) -> dict[str, Any]:
    """Compare labelled volumes and return a JSON-serialisable inspection report."""

    reference = np.asarray(reference)
    candidate = np.asarray(candidate)
    _validate(reference, candidate, voxel_size_um)
    if min_component_voxels < 1:
        raise ValueError("min_component_voxels must be at least 1")

    components: list[ComponentMeasurement] = []
    material_metrics: dict[str, dict[str, float | int]] = {}
    for material in (
        Material.SILICON_DIOXIDE,
        Material.COPPER,
        Material.SAC305_SOLDER,
    ):
        ref_mask = reference == material.value
        candidate_mask = candidate == material.value
        ref_count = int(ref_mask.sum())
        candidate_count = int(candidate_mask.sum())
        intersection = int(np.logical_and(ref_mask, candidate_mask).sum())
        union = int(np.logical_or(ref_mask, candidate_mask).sum())
        material_metrics[material.name.lower()] = {
            "reference_voxels": ref_count,
            "candidate_voxels": candidate_count,
            "intersection_over_union": intersection / union if union else 1.0,
            "dice": (2 * intersection / (ref_count + candidate_count))
            if ref_count + candidate_count
            else 1.0,
            "missing_voxels": int(np.logical_and(ref_mask, ~candidate_mask).sum()),
            "excess_voxels": int(np.logical_and(~ref_mask, candidate_mask).sum()),
        }
        components.extend(
            _components(
                np.logical_and(ref_mask, ~candidate_mask),
                material=material,
                difference="missing",
                material_voxels=ref_count,
                voxel_size_um=voxel_size_um,
                min_component_voxels=min_component_voxels,
            )
        )
        components.extend(
            _components(
                np.logical_and(~ref_mask, candidate_mask),
                material=material,
                difference="excess",
                material_voxels=ref_count,
                voxel_size_um=voxel_size_um,
                min_component_voxels=min_component_voxels,
            )
        )

    severity_order = {"critical": 0, "major": 1, "minor": 2}
    components.sort(key=lambda item: (severity_order[item.severity], -item.voxel_count))
    defects = []
    for index, component in enumerate(components, start=1):
        values = asdict(component)
        values["defect_id"] = f"D{index:04d}"
        defects.append(values)

    return {
        "schema_version": "1.0",
        "method": "labelled_reference_difference_with_26_connectivity",
        "disclaimer": "Root causes are hypotheses for screening and require process evidence.",
        "volume": {
            "shape_zyx": list(reference.shape),
            "voxel_size_um": float(voxel_size_um),
            "total_voxels": int(reference.size),
        },
        "summary": {
            "defect_count": len(defects),
            "critical": sum(item["severity"] == "critical" for item in defects),
            "major": sum(item["severity"] == "major" for item in defects),
            "minor": sum(item["severity"] == "minor" for item in defects),
        },
        "material_metrics": material_metrics,
        "defects": defects,
    }


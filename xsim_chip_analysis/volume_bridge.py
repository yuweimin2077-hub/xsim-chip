"""Join reconstructed slice stacks to the existing three-dimensional inspector."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import ndimage

from .inspection import Material, analyze_against_reference
from .slice_inspection import DEFECT_TYPES, _pixel_metrics, segment_material_slice


def inspect_reconstructed_volume(
    reference: np.ndarray, reconstruction: np.ndarray, *,
    voxel_size_um: float = 16.0, min_component_voxels: int = 8,
) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, Any]]:
    """Segment every reconstructed slice and feed the actual stack to 3D analysis.

    Returns the segmented stack, three screening masks, and the original 3D
    report (all six material-difference signatures). Component filtering of
    screening masks uses the report's same 26-connectivity and voxel limit.
    """

    reconstruction = np.asarray(reconstruction)
    if reconstruction.ndim != 3 or not reconstruction.size:
        raise ValueError("reconstruction must be a non-empty 3D (z, y, x) array")
    if not isinstance(min_component_voxels, int) or min_component_voxels < 1:
        raise ValueError("min_component_voxels must be a positive integer")
    segmented = np.stack([segment_material_slice(image) for image in reconstruction])
    reference = np.asarray(reference)
    report = analyze_against_reference(
        reference, segmented, voxel_size_um=voxel_size_um,
        min_component_voxels=min_component_voxels,
    )
    solder, copper = Material.SAC305_SOLDER.value, Material.COPPER.value
    raw_masks = {
        "solder_void": (reference == solder) & (segmented != solder),
        "solder_bridge": (reference != solder) & (segmented == solder),
        "copper_open": (reference == copper) & (segmented != copper),
    }
    masks = {}
    for kind, raw in raw_masks.items():
        components, _ = ndimage.label(raw, structure=np.ones((3, 3, 3), dtype=bool))
        keep = np.bincount(components.ravel()) >= min_component_voxels
        keep[0] = False
        masks[kind] = keep[components]
    report["input_provenance"] = {
        "candidate": "fixed_threshold_segmentation_of_reconstructed_slice_stack",
        "thresholds": [0.075, 0.40, 0.80],
        "geometry": "slice_wise_parallel_beam_no_z_mixing",
        "min_component_voxels": min_component_voxels,
        "connectivity": 26,
    }
    return segmented, masks, report


def evaluate_volume_defects(
    predicted: dict[str, np.ndarray], truth: dict[str, np.ndarray], *,
    voxel_size_um: float = 16.0,
) -> dict[str, Any]:
    """Strict 3D voxel overlap and aggregate volume error for each signature.

    Evaluation does not modify segmentation, masks, or report components.
    Aggregate signature volume includes all retained false-positive regions.
    """

    if set(predicted) != set(DEFECT_TYPES) or set(truth) != set(DEFECT_TYPES):
        raise ValueError("both dictionaries must contain the three demo defect types")
    arrays = [np.asarray(masks[kind]) for masks in (predicted, truth) for kind in DEFECT_TYPES]
    shape = arrays[0].shape
    if any(a.ndim != 3 or a.shape != shape or not a.size or a.dtype != np.bool_ for a in arrays):
        raise ValueError("all masks must be non-empty boolean 3D arrays of one shape")
    if not np.isfinite(voxel_size_um) or voxel_size_um <= 0:
        raise ValueError("voxel_size_um must be positive and finite")

    def score(p: np.ndarray, t: np.ndarray) -> dict[str, Any]:
        metrics = {key.replace("pixels", "voxels"): value for key, value in _pixel_metrics(p, t).items()}
        predicted_count, truth_count = int(p.sum()), int(t.sum())
        metrics.update({
            "predicted_voxels": predicted_count, "truth_voxels": truth_count,
            "predicted_volume_um3": predicted_count * voxel_size_um**3,
            "truth_volume_um3": truth_count * voxel_size_um**3,
            "relative_volume_error": (predicted_count - truth_count) / truth_count if truth_count else None,
        })
        return metrics

    return {
        "metric_scope": "strict_3d_voxel_overlap_for_three_retained_material_signatures",
        "per_defect": {kind: score(predicted[kind], truth[kind]) for kind in DEFECT_TYPES},
        "union": score(np.logical_or.reduce(list(predicted.values())),
                       np.logical_or.reduce(list(truth.values()))),
    }

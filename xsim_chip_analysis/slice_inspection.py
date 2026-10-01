"""A fixed-threshold 2D baseline linking XCT reconstruction to inspection.

The input is a reconstructed relative-attenuation image, not candidate truth
labels. Reference and reconstruction must already share the same coordinates.
Truth masks are used only by the separate evaluation function.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import ndimage

from .inspection import Material


MATERIAL_THRESHOLDS = (0.075, 0.40, 0.80)
DEFECT_TYPES = ("solder_void", "solder_bridge", "copper_open")


def segment_material_slice(reconstruction: np.ndarray) -> np.ndarray:
    """Assign labels using midpoints of the phantom's 0/.15/.65/.95 levels.

    Thresholds are fixed before evaluation; neither truth labels nor a
    per-image max normalization are used to fit them. Negative FBP values
    map to vacuum. This baseline is specific to the relative-attenuation
    phantom and is not a calibrated real-scanner material classifier.
    """

    image = np.asarray(reconstruction)
    if image.ndim != 2 or not image.size or not np.isfinite(image).all():
        raise ValueError("reconstruction must be a non-empty finite 2D array")
    labels = np.array([item.value for item in Material], dtype=np.uint8)
    return labels[np.digitize(image, MATERIAL_THRESHOLDS)]


def inspect_reconstructed_slice(
    reference: np.ndarray,
    reconstruction: np.ndarray,
    *,
    pixel_size_um: float = 16.0,
    min_component_pixels: int = 4,
) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, Any]]:
    """Compare an aligned reconstructed slice to known-good reference labels.

    Missing solder, excess solder, and missing copper are screening
    signatures. Areas are 2D square micrometres, never 3D defect volumes.
    Small components are removed by the same fixed rule for every signature.
    """

    segmented = segment_material_slice(reconstruction)
    reference = np.asarray(reference)
    if reference.shape != segmented.shape:
        raise ValueError("reference and reconstruction must have the same 2D shape")
    if not np.isin(reference, [item.value for item in Material]).all():
        raise ValueError("reference contains unknown material labels")
    if not np.isfinite(pixel_size_um) or pixel_size_um <= 0:
        raise ValueError("pixel_size_um must be positive and finite")
    if not isinstance(min_component_pixels, int) or min_component_pixels < 1:
        raise ValueError("min_component_pixels must be a positive integer")

    solder = Material.SAC305_SOLDER.value
    copper = Material.COPPER.value
    raw_masks = {
        "solder_void": (reference == solder) & (segmented != solder),
        "solder_bridge": (reference != solder) & (segmented == solder),
        "copper_open": (reference == copper) & (segmented != copper),
    }
    masks: dict[str, np.ndarray] = {}
    components = []
    for kind, mask in raw_masks.items():
        labelled, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=bool))
        sizes = np.bincount(labelled.ravel())
        keep = sizes >= min_component_pixels
        keep[0] = False
        masks[kind] = keep[labelled]
        for label in range(1, count + 1):
            if not keep[label]:
                continue
            positions = np.argwhere(labelled == label)
            centroid = positions.mean(axis=0)
            components.append({
                "defect_kind": kind,
                "pixel_count": int(sizes[label]),
                "area_um2": float(sizes[label] * pixel_size_um**2),
                "centroid_yx_pixels": centroid.tolist(),
                "centroid_yx_um": (centroid * pixel_size_um).tolist(),
            })

    union = np.logical_or.reduce(list(masks.values()))
    report = {
        "method": "fixed_material_thresholds_then_aligned_reference_difference_2d",
        "thresholds": list(MATERIAL_THRESHOLDS),
        "shape_yx": list(segmented.shape),
        "pixel_size_um": float(pixel_size_um),
        "min_component_pixels": min_component_pixels,
        "summary": {
            "component_count": len(components),
            "suspected_defect_pixels": int(union.sum()),
            "suspected_defect_area_um2": float(union.sum() * pixel_size_um**2),
        },
        "components": components,
        "limitations": (
            "Aligned synthetic 2D screening baseline; boundaries and partial-volume "
            "effects can cause false positives. No measured 3D defect volume or "
            "causal diagnosis is inferred."
        ),
    }
    return segmented, masks, report


def _pixel_metrics(predicted: np.ndarray, truth: np.ndarray) -> dict[str, Any]:
    tp = int((predicted & truth).sum())
    fp = int((predicted & ~truth).sum())
    fn = int((~predicted & truth).sum())
    return {
        "true_positive_pixels": tp,
        "false_positive_pixels": fp,
        "false_negative_pixels": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "dice": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 1.0,
        "iou": tp / (tp + fp + fn) if tp + fp + fn else 1.0,
    }


def evaluate_defect_masks(
    predicted_masks: dict[str, np.ndarray],
    truth_masks: dict[str, np.ndarray],
) -> dict[str, Any]:
    """Score strict pixel overlap without using truth to modify predictions."""

    if set(predicted_masks) != set(DEFECT_TYPES) or set(truth_masks) != set(DEFECT_TYPES):
        raise ValueError("both mask dictionaries must contain the three demo defect types")
    arrays = [np.asarray(masks[kind]) for masks in (predicted_masks, truth_masks)
              for kind in DEFECT_TYPES]
    shape = arrays[0].shape
    if any(array.ndim != 2 or array.shape != shape or not array.size
           or array.dtype != np.bool_ for array in arrays):
        raise ValueError("all defect masks must be non-empty boolean 2D arrays of one shape")
    return {
        "metric_scope": "strict_2d_pixel_overlap_not_object_detection_accuracy",
        "per_defect": {
            kind: _pixel_metrics(predicted_masks[kind], truth_masks[kind])
            for kind in DEFECT_TYPES
        },
        "union": _pixel_metrics(
            np.logical_or.reduce([predicted_masks[kind] for kind in DEFECT_TYPES]),
            np.logical_or.reduce([truth_masks[kind] for kind in DEFECT_TYPES]),
        ),
    }

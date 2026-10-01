import json

import numpy as np
import pytest

from xsim_chip_analysis import (
    Material,
    evaluate_defect_masks,
    inject_demo_defects,
    inspect_reconstructed_slice,
    make_package_slice,
    material_to_attenuation,
    segment_material_slice,
)


def test_exact_attenuation_recovers_labels_and_each_injected_defect():
    reference = make_package_slice(129)
    candidate, truth = inject_demo_defects(reference)
    segmented, masks, report = inspect_reconstructed_slice(
        reference, material_to_attenuation(candidate), min_component_pixels=1,
    )
    assert np.array_equal(segmented, candidate)
    for kind in truth:
        assert np.array_equal(masks[kind], truth[kind])
    scores = evaluate_defect_masks(masks, truth)
    assert scores["union"]["dice"] == 1.0
    assert scores["union"]["false_positive_pixels"] == 0
    assert scores["union"]["false_negative_pixels"] == 0
    assert report["summary"]["suspected_defect_area_um2"] == int(
        np.logical_or.reduce(list(truth.values())).sum()
    ) * 16**2
    assert report["summary"]["component_count"] == 3
    assert all(len(component["centroid_yx_pixels"]) == 2 for component in report["components"])
    json.dumps(report)


def test_fixed_thresholds_and_negative_fbp_values():
    segmented = segment_material_slice(np.array([[-0.1, .074, .075, .399, .4, .799, .8]]))
    assert segmented.tolist() == [[0, 0, 85, 85, 170, 170, 255]]


def test_minimum_component_filter_keeps_connected_pixels_and_removes_isolated_noise():
    reference = np.full((8, 8), Material.SAC305_SOLDER, dtype=np.uint8)
    image = material_to_attenuation(reference)
    image[0, 0] = 0
    image[3:5, 3:5] = 0
    _, masks, report = inspect_reconstructed_slice(reference, image)
    assert not masks["solder_void"][0, 0]
    assert int(masks["solder_void"].sum()) == 4
    assert report["summary"]["component_count"] == 1
    assert report["components"][0]["area_um2"] == 1024.0


def test_known_confusion_counts_and_empty_mask_conventions():
    masks = {kind: np.zeros((2, 3), dtype=bool)
             for kind in ("solder_void", "solder_bridge", "copper_open")}
    truth = {kind: array.copy() for kind, array in masks.items()}
    masks["solder_void"][0, :2] = True
    truth["solder_void"][0, 1:] = True
    score = evaluate_defect_masks(masks, truth)
    assert score["union"]["precision"] == .5
    assert score["union"]["recall"] == .5
    assert score["union"]["dice"] == .5
    assert score["union"]["iou"] == pytest.approx(1 / 3)
    assert score["per_defect"]["solder_bridge"]["precision"] is None
    assert score["per_defect"]["solder_bridge"]["recall"] is None
    assert score["per_defect"]["solder_bridge"]["dice"] == 1


@pytest.mark.parametrize("image", [np.zeros((3, 3, 3)), np.empty((0, 2)),
                                 np.array([[np.nan]]), np.array([[np.inf]])])
def test_reconstruction_validation(image):
    with pytest.raises(ValueError, match="finite 2D"):
        segment_material_slice(image)


@pytest.mark.parametrize("kwargs", [{"pixel_size_um": 0}, {"pixel_size_um": np.nan},
                                  {"min_component_pixels": 0},
                                  {"min_component_pixels": 1.5}])
def test_inspection_settings_validation(kwargs):
    with pytest.raises(ValueError):
        inspect_reconstructed_slice(np.zeros((2, 2)), np.zeros((2, 2)), **kwargs)


def test_reference_shape_and_label_validation():
    with pytest.raises(ValueError, match="same 2D shape"):
        inspect_reconstructed_slice(np.zeros((3, 2)), np.zeros((2, 2)))
    with pytest.raises(ValueError, match="unknown material"):
        inspect_reconstructed_slice(np.full((2, 2), 42), np.zeros((2, 2)))


def test_truth_validation():
    names = ("solder_void", "solder_bridge", "copper_open")
    masks = {kind: np.zeros((2, 2), dtype=bool) for kind in names}
    with pytest.raises(ValueError, match="three demo"):
        evaluate_defect_masks({}, masks)
    for malformed in (np.zeros((3, 2), dtype=bool), np.zeros((2, 2), dtype=int),
                      np.empty((0, 2), dtype=bool)):
        bad = {**masks, "solder_void": malformed}
        with pytest.raises(ValueError, match="boolean 2D"):
            evaluate_defect_masks(bad, masks)

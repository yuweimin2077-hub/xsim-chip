import json

import numpy as np
import pytest

from xsim_chip_analysis import (
    evaluate_volume_defects, inspect_reconstructed_volume, make_demo_volume,
    material_to_attenuation,
)


def test_phantom_has_distinct_depth_intervals_and_exact_truth():
    reference, candidate, truth = make_demo_volume()
    assert reference.shape == candidate.shape == (16, 129, 129)
    assert {kind: int(mask.sum()) for kind, mask in truth.items()} == {
        "solder_void": 104, "solder_bridge": 528, "copper_open": 240,
    }
    assert np.array_equal(np.logical_or.reduce(list(truth.values())), reference != candidate)
    assert np.array_equal(reference[0], candidate[0])
    assert not np.array_equal(candidate[4], candidate[8])
    assert not np.array_equal(candidate[8], candidate[12])
    again = make_demo_volume()
    assert np.array_equal(candidate, again[1])


def test_exact_attenuation_stack_flows_to_3d_report_and_volume_metrics():
    reference, candidate, truth = make_demo_volume()
    segmented, predicted, report = inspect_reconstructed_volume(
        reference, material_to_attenuation(candidate),
    )
    assert np.array_equal(segmented, candidate)
    for kind in truth:
        assert np.array_equal(predicted[kind], truth[kind])
    metrics = evaluate_volume_defects(predicted, truth)
    assert metrics["union"]["dice"] == 1.0
    assert metrics["union"]["relative_volume_error"] == 0.0
    assert metrics["per_defect"]["solder_void"]["truth_volume_um3"] == 104 * 16**3
    void = next(d for d in report["defects"] if d["defect_kind"] == "solder_void_or_open")
    assert void["bounding_box_zyx"][0] == (4, 12)
    assert void["volume_um3"] == 104 * 16**3
    assert report["input_provenance"]["connectivity"] == 26
    json.dumps(report)


def test_3d_filter_connects_across_slices_and_rejects_isolated_voxel():
    reference = np.full((8, 4, 4), 255, dtype=np.uint8)
    reconstruction = material_to_attenuation(reference)
    reconstruction[:, 2, 2] = 0  # one pixel per slice, but eight connected voxels
    reconstruction[0, 0, 0] = 0
    _, masks, report = inspect_reconstructed_volume(reference, reconstruction)
    assert int(masks["solder_void"].sum()) == 8
    assert not masks["solder_void"][0, 0, 0]
    assert report["summary"]["defect_count"] == 1


def test_copying_one_reconstructed_slice_cannot_recover_depth_localisation():
    reference, candidate, truth = make_demo_volume()
    copied = np.repeat(material_to_attenuation(candidate[0])[None], 16, axis=0)
    _, masks, _ = inspect_reconstructed_volume(reference, copied)
    score = evaluate_volume_defects(masks, truth)
    assert score["union"]["recall"] == 0.0
    assert score["union"]["false_negative_voxels"] == 872


@pytest.mark.parametrize("depth", [0, 7, 8.5])
def test_phantom_rejects_invalid_depth(depth):
    with pytest.raises(ValueError, match="depth"):
        make_demo_volume(depth=depth)


@pytest.mark.parametrize("bad", [np.zeros((2, 2)), np.empty((0, 2, 2))])
def test_reconstruction_stack_validation(bad):
    with pytest.raises(ValueError, match="non-empty 3D"):
        inspect_reconstructed_volume(np.zeros((2, 2, 2)), bad)


def test_volume_component_limit_validation():
    with pytest.raises(ValueError, match="positive integer"):
        inspect_reconstructed_volume(np.zeros((2, 2, 2)), np.zeros((2, 2, 2)), min_component_voxels=1.5)


def test_evaluation_empty_masks_and_validation():
    names = ("solder_void", "solder_bridge", "copper_open")
    masks = {kind: np.zeros((2, 2, 2), dtype=bool) for kind in names}
    score = evaluate_volume_defects(masks, masks)["union"]
    assert score["dice"] == 1.0
    assert score["precision"] is None
    assert score["relative_volume_error"] is None
    with pytest.raises(ValueError, match="three demo"):
        evaluate_volume_defects({}, masks)
    with pytest.raises(ValueError, match="boolean 3D"):
        evaluate_volume_defects({**masks, "solder_void": np.zeros((2, 2), dtype=bool)}, masks)
    with pytest.raises(ValueError, match="positive and finite"):
        evaluate_volume_defects(masks, masks, voxel_size_um=0)

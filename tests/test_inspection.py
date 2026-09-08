import json
import sys

import numpy as np
import pytest

from xsim_chip_analysis import Material, analyze_against_reference
from xsim_chip_analysis.cli import main


def make_reference() -> np.ndarray:
    volume = np.zeros((24, 24, 24), dtype=np.uint8)
    volume[2:22, 2:22, 2:22] = Material.SILICON_DIOXIDE
    volume[6:18, 6:18, 6:18] = Material.COPPER
    volume[9:15, 9:15, 9:15] = Material.SAC305_SOLDER
    return volume


def test_detects_solder_void_and_bridge_as_separate_components() -> None:
    reference = make_reference()
    candidate = reference.copy()
    candidate[10:12, 10:12, 10:12] = Material.VACUUM
    candidate[15:17, 15:17, 15:17] = Material.SAC305_SOLDER

    report = analyze_against_reference(reference, candidate, min_component_voxels=2)

    kinds = {defect["defect_kind"] for defect in report["defects"]}
    assert {"solder_void_or_open", "solder_bridge"} <= kinds
    assert report["summary"]["defect_count"] >= 2
    solder = report["material_metrics"]["sac305_solder"]
    assert solder["missing_voxels"] == 8
    assert solder["excess_voxels"] == 8


def test_filters_single_voxel_noise() -> None:
    reference = make_reference()
    candidate = reference.copy()
    candidate[10, 10, 10] = Material.VACUUM

    report = analyze_against_reference(reference, candidate, min_component_voxels=2)

    assert report["summary"]["defect_count"] == 0
    assert report["material_metrics"]["sac305_solder"]["missing_voxels"] == 1


def test_rejects_invalid_shapes_and_labels() -> None:
    reference = make_reference()
    with pytest.raises(ValueError, match="shapes differ"):
        analyze_against_reference(reference, reference[:2])

    candidate = reference.copy()
    candidate[0, 0, 0] = 42
    with pytest.raises(ValueError, match="unknown material labels"):
        analyze_against_reference(reference, candidate)


def test_cli_writes_json_report(tmp_path, monkeypatch, capsys) -> None:
    reference = make_reference()
    candidate = reference.copy()
    candidate[10:12, 10:12, 10:12] = Material.VACUUM
    reference_path = tmp_path / "reference.npy"
    candidate_path = tmp_path / "candidate.npy"
    output_path = tmp_path / "reports" / "inspection.json"
    np.save(reference_path, reference)
    np.save(candidate_path, candidate)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "xsim-inspect",
            str(reference_path),
            str(candidate_path),
            "--output",
            str(output_path),
            "--min-component-voxels",
            "2",
        ],
    )

    main()

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["summary"]["defect_count"] >= 1
    assert "Report written" in capsys.readouterr().out


def test_cli_rejects_unknown_file_format(tmp_path, monkeypatch) -> None:
    unknown = tmp_path / "volume.raw"
    unknown.write_bytes(b"not a supported volume")
    monkeypatch.setattr(sys, "argv", ["xsim-inspect", str(unknown), str(unknown)])

    with pytest.raises(ValueError, match="unsupported volume format"):
        main()


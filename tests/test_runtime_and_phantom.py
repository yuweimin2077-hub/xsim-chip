import numpy as np
import pytest

from xsim_chip_analysis import (
    ConeBeamConfig,
    Material,
    SimulationConfig,
    SpectrumConfig,
    build_run_manifest,
    estimate_memory,
    inject_demo_defects,
    make_package_slice,
    material_to_attenuation,
    normalise_energy_image,
    summarise_spectrum,
)


def test_quick_profile_is_far_smaller_than_nist_reference() -> None:
    quick = estimate_memory(SimulationConfig.quick_colab())
    full = estimate_memory(SimulationConfig.nist_reference())

    assert quick["declared_numpy_buffers_gib"] < 0.2
    assert full["declared_numpy_buffers_gib"] > 15
    assert quick["declared_numpy_buffers_gib"] < full["declared_numpy_buffers_gib"] / 100


@pytest.mark.parametrize(
    "kwargs",
    [
        {"volume_shape_zyx": (0, 2, 3)},
        {"detector_shape_rc": (2, -1)},
        {"projections": 0},
        {"voxel_size_um": float("nan")},
    ],
)
def test_config_rejects_invalid_values(kwargs) -> None:
    values = {
        "profile": "invalid",
        "volume_shape_zyx": (3, 3, 3),
        "detector_shape_rc": (3, 3),
        "projections": 2,
        "voxel_size_um": 4.0,
        "seed": 1,
    }
    values.update(kwargs)
    with pytest.raises(ValueError):
        SimulationConfig(**values)


def test_package_slice_and_defects_are_deterministic() -> None:
    first = make_package_slice(128, seed=7)
    second = make_package_slice(128, seed=7)
    candidate, truth = inject_demo_defects(first)

    assert np.array_equal(first, second)
    assert first.dtype == np.uint8
    assert set(np.unique(first)) <= {item.value for item in Material}
    assert set(truth) == {"solder_void", "solder_bridge", "copper_open"}
    assert all(mask.any() for mask in truth.values())
    assert not np.array_equal(first, candidate)


def test_attenuation_orders_package_materials() -> None:
    labels = np.array(
        [[Material.VACUUM, Material.SILICON_DIOXIDE, Material.COPPER, Material.SAC305_SOLDER]],
        dtype=np.uint8,
    )
    values = material_to_attenuation(labels)[0]

    assert np.all(np.diff(values) > 0)
    with pytest.raises(ValueError, match="unknown material labels"):
        material_to_attenuation(np.array([[42]], dtype=np.uint8))


def test_manifest_is_serialisable_and_reports_missing_optional_packages(monkeypatch) -> None:
    monkeypatch.delenv("COLAB_RELEASE_TAG", raising=False)
    manifest = build_run_manifest(
        SimulationConfig.quick_colab(), packages=("numpy", "definitely-not-installed")
    )

    assert manifest["config"]["profile"] == "quick-colab"
    assert manifest["runtime"]["is_google_colab"] is False
    assert manifest["packages"]["numpy"]
    assert manifest["packages"]["definitely-not-installed"] is None


def test_phantom_input_validation() -> None:
    with pytest.raises(ValueError, match="at least 64"):
        make_package_slice(32)
    with pytest.raises(ValueError, match="square 2D"):
        inject_demo_defects(np.zeros((3, 4), dtype=np.uint8))


def test_spectral_and_cone_beam_configs_are_manifest_ready() -> None:
    spectrum = SpectrumConfig()
    geometry = ConeBeamConfig()

    assert spectrum.to_manifest()["filters_mm"][1] == {
        "element": "Cu",
        "thickness_mm": 1.0,
    }
    assert geometry.magnification == pytest.approx(3.0)
    assert geometry.object_pixel_size_mm == pytest.approx((0.16 / 3, 0.16 / 3))


@pytest.mark.parametrize(
    "factory",
    [
        lambda: SpectrumConfig(tube_voltage_kv=0),
        lambda: SpectrumConfig(tube_voltage_kv=4, energy_bin_size_kev=4),
        lambda: SpectrumConfig(filters_mm=(("Cu", -1.0),)),
        lambda: ConeBeamConfig(detector_pixels_xy=(0, 10)),
        lambda: ConeBeamConfig(source_position_mm=(1.0, 0.0, 0.0)),
    ],
)
def test_spectral_configs_reject_invalid_values(factory) -> None:
    with pytest.raises(ValueError):
        factory()


def test_spectrum_summary_and_energy_normalisation() -> None:
    energy = np.array([20.0, 40.0, 80.0])
    counts = np.array([1.0, 2.0, 1.0])
    summary = summarise_spectrum(energy, counts)

    assert summary["bins"] == 3
    assert summary["mean_energy_kev"] == pytest.approx(45.0)
    assert summary["fraction_below_40_kev"] == pytest.approx(0.25)
    result = normalise_energy_image(np.array([[0.0, 5.0], [10.0, 20.0]]), 10.0)
    assert np.array_equal(result, np.array([[0.0, 0.5], [1.0, 1.0]], dtype=np.float32))


@pytest.mark.parametrize(
    "energy,counts",
    [
        ([20.0], [0.0]),
        ([20.0, 40.0], [1.0]),
        ([-20.0], [1.0]),
        ([20.0], [float("nan")]),
    ],
)
def test_spectrum_summary_rejects_invalid_arrays(energy, counts) -> None:
    with pytest.raises(ValueError):
        summarise_spectrum(np.asarray(energy), np.asarray(counts))


def test_energy_normalisation_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        normalise_energy_image(np.zeros((2, 2, 2)), 1.0)
    with pytest.raises(ValueError):
        normalise_energy_image(np.zeros((2, 2)), 0.0)

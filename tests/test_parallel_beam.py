import numpy as np
import pytest

from xsim_chip_analysis import (
    material_to_attenuation, make_package_slice, reconstruct_parallel_sinogram,
    reconstruct_projection_stack, simulate_parallel_projection,
)


@pytest.mark.parametrize("bad", [np.zeros((2, 3)), np.zeros((2, 2, 2)),
                                 np.array([[np.nan]]), np.array([[-1.0]])])
def test_projection_input_validation(bad):
    with pytest.raises(ValueError, match="square 2D"):
        simulate_parallel_projection(bad)


@pytest.mark.parametrize("kwargs", [{"views": 0}, {"detector_bins": 1.5},
                                  {"photons": 0}, {"pixel_size_um": 0}])
def test_acquisition_parameter_validation(kwargs):
    with pytest.raises(ValueError):
        simulate_parallel_projection(np.zeros((8, 8)), **kwargs)


def test_sinogram_and_stack_validation():
    with pytest.raises(ValueError, match="finite 2D"):
        reconstruct_parallel_sinogram(np.array([[np.nan]]), size=8)
    with pytest.raises(ValueError, match="positive integer"):
        reconstruct_parallel_sinogram(np.zeros((4, 8)), size=0)
    with pytest.raises(ValueError, match="angle, z, bin"):
        reconstruct_projection_stack(np.zeros((4, 8)), size=8)


def test_real_cpu_projection_and_reconstruction_preserve_scale_and_seed():
    pytest.importorskip("astra")
    attenuation = material_to_attenuation(make_package_slice(64))
    sino, info = simulate_parallel_projection(attenuation, views=90, detector_bins=96, use_cuda=False)
    repeat, _ = simulate_parallel_projection(attenuation, views=90, detector_bins=96, use_cuda=False)
    assert np.array_equal(sino, repeat)
    reconstructed, meta = reconstruct_parallel_sinogram(sino, size=64, use_cuda=False)
    assert sino.shape == (90, 96)
    assert reconstructed.shape == attenuation.shape
    assert info["zero_count_rays"] == 0
    assert meta["algorithm"] == "FBP"
    assert np.sqrt(np.mean((attenuation - reconstructed)**2)) / .95 < .15


def test_each_projection_row_drives_its_own_reconstructed_slice():
    pytest.importorskip("astra")
    phantom = np.zeros((32, 32), dtype=np.float32)
    phantom[10:22, 10:22] = .65
    sino, _ = simulate_parallel_projection(phantom, views=60, detector_bins=48, use_cuda=False)
    projections = np.stack([np.zeros_like(sino), sino, 2 * sino], axis=1)
    volume, metadata = reconstruct_projection_stack(projections, size=32, use_cuda=False)
    assert volume.shape == (3, 32, 32)
    assert np.all(volume[0] == 0)
    assert float(volume[1].max()) > .5
    np.testing.assert_allclose(volume[2], 2 * volume[1], atol=1e-5)
    assert [row["z_index"] for row in metadata] == [0, 1, 2]


def test_explicit_cuda_request_fails_if_unavailable(monkeypatch):
    astra = pytest.importorskip("astra")
    monkeypatch.setattr(astra, "use_cuda", lambda: False)
    with pytest.raises(RuntimeError, match="CUDA requested"):
        simulate_parallel_projection(np.zeros((8, 8)), use_cuda=True)


def test_cuda_path_when_available():
    astra = pytest.importorskip("astra")
    if not astra.use_cuda():
        pytest.skip("CUDA hardware unavailable; CPU path is always tested")
    phantom = np.zeros((32, 32), dtype=np.float32)
    phantom[10:22, 10:22] = .65
    sino, _ = simulate_parallel_projection(phantom, views=60, detector_bins=48)
    image, info = reconstruct_parallel_sinogram(sino, size=32)
    assert info["algorithm"] == "FBP_CUDA"
    assert float(image.max()) > .5

"""Shared ASTRA parallel-beam operations for the 2D and slice-wise 3D demos.

Reconstruction accepts projection data and geometry only. Simulation truth
never enters reconstruction or threshold fitting. ASTRA is an optional import.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np


def _positive(value: float, name: str) -> None:
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")


def _geometry(size: int, views: int, bins: int, use_cuda: bool | None):
    import astra

    cuda = bool(astra.use_cuda()) if use_cuda is None else use_cuda
    if cuda and not astra.use_cuda():
        raise RuntimeError("CUDA requested but unavailable to ASTRA")
    angles = np.linspace(0, np.pi, views, endpoint=False)
    projection = astra.create_proj_geom("parallel", 1.0, bins, angles)
    volume = astra.create_vol_geom(size, size)
    projector = astra.create_projector("cuda" if cuda else "linear", projection, volume)
    return astra, cuda, projection, volume, projector


def simulate_parallel_projection(
    attenuation: np.ndarray, *, pixel_size_um: float = 16.0,
    views: int = 180, detector_bins: int = 192, photons: int = 100_000,
    seed: int = 2060, use_cuda: bool | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Simulate a noisy sinogram (angle, bin) on a unit-pixel ASTRA grid."""

    attenuation = np.asarray(attenuation, dtype=np.float32)
    if (attenuation.ndim != 2 or not attenuation.size
            or attenuation.shape[0] != attenuation.shape[1]
            or not np.isfinite(attenuation).all() or np.any(attenuation < 0)):
        raise ValueError("attenuation must be a non-empty finite nonnegative square 2D array")
    _positive(pixel_size_um, "pixel_size_um")
    for value, name in ((views, "views"), (detector_bins, "detector_bins"), (photons, "photons")):
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    started = time.perf_counter()
    astra, cuda, _, _, projector = _geometry(
        attenuation.shape[0], views, detector_bins, use_cuda,
    )
    sino_id = None
    try:
        sino_id, optical_depth = astra.create_sino(attenuation * (pixel_size_um / 1000.0), projector)
        transmission = np.exp(-np.clip(optical_depth, 0, None))
        counts = np.random.default_rng(seed).poisson(transmission * photons)
        sinogram = -np.log(np.clip(counts / photons, 1 / photons, 1.0)).astype(np.float32)
    finally:
        if sino_id is not None:
            astra.data2d.delete(sino_id)
        astra.projector.delete(projector)
    return sinogram, {
        "projector": "cuda" if cuda else "linear", "seed": seed,
        "photons": photons, "zero_count_rays": int((counts == 0).sum()),
        "projection_noise_seconds": time.perf_counter() - started,
    }


def reconstruct_parallel_sinogram(
    sinogram: np.ndarray, *, size: int, pixel_size_um: float = 16.0,
    use_cuda: bool | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Reconstruct from a measured/simulated sinogram, without truth labels."""

    sinogram = np.asarray(sinogram, dtype=np.float32)
    if sinogram.ndim != 2 or not sinogram.size or not np.isfinite(sinogram).all():
        raise ValueError("sinogram must be a non-empty finite 2D array")
    if not isinstance(size, int) or size < 1:
        raise ValueError("size must be a positive integer")
    _positive(pixel_size_um, "pixel_size_um")
    astra, cuda, projection, volume, projector = _geometry(size, *sinogram.shape, use_cuda)
    sino_id = recon_id = algorithm_id = None
    try:
        sino_id = astra.data2d.create("-sino", projection, sinogram)
        recon_id = astra.data2d.create("-vol", volume)
        algorithm = "FBP_CUDA" if cuda else "FBP"
        cfg = astra.astra_dict(algorithm)
        cfg["ProjectionDataId"] = sino_id
        cfg["ReconstructionDataId"] = recon_id
        cfg["option"] = {"FilterType": "hann"}
        if not cuda:
            cfg["ProjectorId"] = projector
        algorithm_id = astra.algorithm.create(cfg)
        started = time.perf_counter()
        astra.algorithm.run(algorithm_id)
        reconstruction = astra.data2d.get(recon_id).astype(np.float32)
        elapsed = time.perf_counter() - started
    finally:
        if algorithm_id is not None:
            astra.algorithm.delete(algorithm_id)
        astra.data2d.delete([item for item in (sino_id, recon_id) if item is not None])
        astra.projector.delete(projector)
    return np.clip(reconstruction / (pixel_size_um / 1000.0), 0, None), {
        "algorithm": algorithm, "filter": "hann", "fbp_run_and_readback_seconds": elapsed,
    }


def reconstruct_projection_stack(
    projections: np.ndarray, *, size: int, voxel_size_um: float = 16.0,
    use_cuda: bool | None = None,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Reconstruct every detector row of an (angle, z, bin) parallel stack.

    Parallel rays have zero z component, and each detector row corresponds to
    one slice with the same isotropic spacing. There is no cone divergence,
    z mixing, registration, or interpolation of a single reconstructed slice.
    """

    projections = np.asarray(projections)
    if projections.ndim != 3 or not projections.size or not np.isfinite(projections).all():
        raise ValueError("projections must be a non-empty finite (angle, z, bin) array")
    reconstructed, metadata = [], []
    for z in range(projections.shape[1]):
        image, info = reconstruct_parallel_sinogram(
            projections[:, z, :], size=size, pixel_size_um=voxel_size_um, use_cuda=use_cuda,
        )
        reconstructed.append(image)
        metadata.append({"z_index": z, **info})
    return np.stack(reconstructed), metadata

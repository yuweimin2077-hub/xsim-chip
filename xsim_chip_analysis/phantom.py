"""Small deterministic package cross-sections for XCT smoke experiments."""

from __future__ import annotations

import numpy as np

from .inspection import Material


def _disk(shape: tuple[int, int], center: tuple[int, int], radius: int) -> np.ndarray:
    yy, xx = np.ogrid[: shape[0], : shape[1]]
    return (yy - center[0]) ** 2 + (xx - center[1]) ** 2 <= radius**2


def make_package_slice(size: int = 256, seed: int = 2060) -> np.ndarray:
    """Generate a material-labelled 2D package cross-section.

    The layout is intentionally compact for Colab validation and is not a
    replacement for the full NIST phantom.
    """

    if not isinstance(size, int) or size < 64:
        raise ValueError("size must be an integer of at least 64")
    rng = np.random.default_rng(seed)
    image = np.zeros((size, size), dtype=np.uint8)
    image[int(0.12 * size) : int(0.84 * size), int(0.08 * size) : int(0.92 * size)] = (
        Material.SILICON_DIOXIDE
    )

    layer_half_width = max(1, size // 128)
    for row_fraction in (0.28, 0.40, 0.52):
        row = int(row_fraction * size)
        image[row - layer_half_width : row + layer_half_width + 1, int(0.1 * size) : int(0.9 * size)] = Material.COPPER

    via_centres = np.linspace(int(0.2 * size), int(0.8 * size), 7, dtype=int)
    via_centres = via_centres + rng.integers(-1, 2, size=via_centres.shape)
    for column in via_centres:
        image[int(0.28 * size) : int(0.53 * size), column - 1 : column + 2] = Material.COPPER

    bump_radius = max(4, int(0.055 * size))
    bump_row = int(0.72 * size)
    for column_fraction in (0.28, 0.50, 0.72):
        image[_disk(image.shape, (bump_row, int(column_fraction * size)), bump_radius)] = Material.SAC305_SOLDER
    return image


def inject_demo_defects(reference: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Inject a solder void, solder bridge, and copper open with truth masks."""

    reference = np.asarray(reference)
    if reference.ndim != 2 or reference.shape[0] != reference.shape[1]:
        raise ValueError("reference must be a square 2D material-label image")
    size = reference.shape[0]
    candidate = reference.copy()
    truth: dict[str, np.ndarray] = {}

    void_mask = _disk(reference.shape, (int(0.72 * size), int(0.50 * size)), max(2, int(0.018 * size)))
    void_mask &= reference == Material.SAC305_SOLDER
    candidate[void_mask] = Material.VACUUM
    truth["solder_void"] = void_mask

    bridge_mask = np.zeros_like(reference, dtype=bool)
    bridge_mask[
        int(0.70 * size) : int(0.74 * size) + 1,
        int(0.55 * size) : int(0.67 * size) + 1,
    ] = True
    bridge_mask &= reference != Material.SAC305_SOLDER
    candidate[bridge_mask] = Material.SAC305_SOLDER
    truth["solder_bridge"] = bridge_mask

    open_mask = np.zeros_like(reference, dtype=bool)
    row = int(0.28 * size)
    half_width = max(1, size // 128)
    open_mask[
        row - half_width : row + half_width + 1,
        int(0.46 * size) : int(0.54 * size),
    ] = reference[
        row - half_width : row + half_width + 1,
        int(0.46 * size) : int(0.54 * size),
    ] == Material.COPPER
    candidate[open_mask] = Material.SILICON_DIOXIDE
    truth["copper_open"] = open_mask
    return candidate, truth


def material_to_attenuation(labels: np.ndarray) -> np.ndarray:
    """Map material labels to relative monoenergetic attenuation coefficients."""

    labels = np.asarray(labels)
    allowed = np.array([item.value for item in Material], dtype=np.int64)
    invalid = np.unique(labels)[~np.isin(np.unique(labels), allowed)]
    if invalid.size:
        raise ValueError(f"unknown material labels: {invalid.tolist()}")
    attenuation = np.zeros(labels.shape, dtype=np.float32)
    attenuation[labels == Material.SILICON_DIOXIDE] = 0.15
    attenuation[labels == Material.COPPER] = 0.65
    attenuation[labels == Material.SAC305_SOLDER] = 0.95
    return attenuation


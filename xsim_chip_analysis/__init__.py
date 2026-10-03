"""Defect inspection extensions for NIST xsim-chip volumes."""

from .inspection import Material, analyze_against_reference
from .phantom import inject_demo_defects, make_demo_volume, make_package_slice, material_to_attenuation
from .parallel_beam import (
    reconstruct_parallel_sinogram, reconstruct_projection_stack, simulate_parallel_projection,
)
from .volume_bridge import evaluate_volume_defects, inspect_reconstructed_volume
from .runtime import SimulationConfig, build_run_manifest, estimate_memory
from .slice_inspection import (
    evaluate_defect_masks,
    inspect_reconstructed_slice,
    segment_material_slice,
)
from .spectral import (
    ConeBeamConfig,
    SpectrumConfig,
    normalise_energy_image,
    summarise_spectrum,
)

__all__ = [
    "Material",
    "ConeBeamConfig",
    "SimulationConfig",
    "SpectrumConfig",
    "analyze_against_reference",
    "build_run_manifest",
    "estimate_memory",
    "evaluate_defect_masks",
    "evaluate_volume_defects",
    "inject_demo_defects",
    "inspect_reconstructed_slice",
    "inspect_reconstructed_volume",
    "make_demo_volume",
    "make_package_slice",
    "material_to_attenuation",
    "normalise_energy_image",
    "segment_material_slice",
    "reconstruct_parallel_sinogram",
    "reconstruct_projection_stack",
    "simulate_parallel_projection",
    "summarise_spectrum",
]

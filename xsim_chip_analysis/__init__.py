"""Defect inspection extensions for NIST xsim-chip volumes."""

from .inspection import Material, analyze_against_reference
from .phantom import inject_demo_defects, make_package_slice, material_to_attenuation
from .runtime import SimulationConfig, build_run_manifest, estimate_memory

__all__ = [
    "Material",
    "SimulationConfig",
    "analyze_against_reference",
    "build_run_manifest",
    "estimate_memory",
    "inject_demo_defects",
    "make_package_slice",
    "material_to_attenuation",
]

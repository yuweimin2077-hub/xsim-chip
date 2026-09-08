# Colab gVXR validation — 2026-09-08

## Environment

- Google Colab T4 GPU
- gVXR core/SimpleGVXR 2.1.0
- OpenGL vendor: NVIDIA Corporation
- OpenGL renderer: Tesla T4/PCIe/SSE2
- OpenGL version: 4.3.0 NVIDIA 580.82.07

## Findings

The Colab dependency installation and Python import path are working. A minimal
single-object gVXR scene renders successfully (`320 x 640` in the official
probe). The project notebook uses `createNewContext()`, which is the context
initialisation path that produced a valid renderer in this runtime.

The initial package-like scene exposed two independent issues:

1. `setMixture` requires element symbols (`['Si', 'O']`), not atomic numbers.
2. After fixing the symbols, the multi-material, polychromatic projection path
   returned an empty array or restarted the Colab kernel on the T4 runtime.

The notebook is therefore reduced to a one-cuboid SiO₂ smoke test at 96 x 64
detector resolution. This keeps the install, cone-beam geometry, spectrum,
filter, validation, plotting, and output-manifest path reproducible. Extending
the smoke test back to the full SiO₂/Cu/SAC305 package is the next engineering
task and should be done incrementally, validating each material and renderer
call separately.

This is a runtime compatibility finding, not evidence that the physical package
model is invalid. The notebook explicitly records the limitation so later
results are not mistaken for a calibrated scanner simulation.

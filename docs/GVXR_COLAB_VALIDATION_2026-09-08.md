# Colab gVXR validation — 2026-09-08

## Environment

- Google Colab T4 GPU
- gVXR core/SimpleGVXR 2.1.0
- OpenGL vendor: NVIDIA Corporation
- OpenGL renderer: Tesla T4/PCIe/SSE2
- OpenGL version: 4.3.0 NVIDIA 580.82.07

## Findings

The Colab dependency installation and Python import path are working. The
official single-object, monochromatic gVXR scene renders successfully
(`320 x 640`). Parameter sweeps showed that detector size, object scale, and
cone-beam geometry were not the cause of the empty projection.

The initial package-like scene exposed two independent issues:

1. `setMixture` requires element symbols (`['Si', 'O']`), not atomic numbers.
2. gVXR 2.1's automatic `setVoltage()` spectrum produced an empty projection
   when configured after the scene and crashed the Colab kernel when moved
   before detector creation.
3. Explicit spectra loaded with `addEnergyBinToSpectrumPerPixelAtSDD()` before
   detector creation produced valid unfiltered and filtered projections with
   the declared `(128, 192)` array shape.

The notebook is therefore reduced to a one-cuboid SiO₂ smoke test using the
declared 192 x 128 detector. It builds a deterministic Kramers continuum,
applies Al/Cu attenuation with gVXR's mass attenuation coefficients, creates a
fresh context for each spectrum, loads every bin explicitly before detector
creation, and validates the exact projection shape before normalisation. The
original empty-array traceback came from a Colab tab pinned to commit
`24c0bc4`; Colab continued to display that cached document even after the
address was changed to `main`.

Users should reopen the notebook from the current `main`-branch Colab badge.
The first cell prints the checked-out Git revision, and the notebook now emits
a direct renderer/cache diagnostic if gVXR returns an empty or incorrectly
sized projection. The Kramers spectrum is deliberately labelled as an
uncalibrated compatibility model. Extending the smoke test back to the full SiO₂/Cu/SAC305
package remains the next engineering task and should be done incrementally,
validating each material and renderer call separately.

This is a runtime compatibility finding, not evidence that the physical package
model is invalid. The notebook explicitly records the limitation so later
results are not mistaken for a calibrated scanner simulation.

# Modification notice

This repository is derived from the National Institute of Standards and
Technology (NIST) `usnistgov/xsim-chip` project. The original NIST software and
its licensing statement remain intact in `LICENSE.md`.

## 2026-09-08

- Added the `xsim_chip_analysis` package for reference-based, material-aware 3D
  defect inspection.
- Added connected-component measurements, physical-unit conversion, severity
  screening, and explicitly non-diagnostic root-cause hypotheses.
- Added a command-line interface, automated tests, Python packaging metadata,
  and a Google Colab quick-start notebook.
- Expanded `.gitignore` for reproducible Python and notebook development.
- Added low-memory and NIST-reference runtime profiles with transparent NumPy
  buffer estimates and reproducibility manifests.
- Added a deterministic package cross-section with controlled solder-void,
  solder-bridge, and copper-open ground truth.
- Added an ASTRA Colab notebook for parallel-beam forward projection, simulated
  photon noise, CUDA/CPU filtered backprojection, metrics, and saved artefacts.
- Declared Python 3.11–3.14 support for the analysis package and added Python
  3.13 CI coverage for compatibility with the current Colab runtime.
- Executed the reduced simulation on a Colab Tesla T4 with ASTRA 2.5.0,
  archived the reproducibility manifest and result summary, and verified the
  CUDA `FBP_CUDA` path end to end.
- Added validated spectral and cone-beam configuration objects plus spectrum
  summary and flat-field normalisation utilities.
- Added a Colab-first gVXR notebook comparing unfiltered and Al/Cu-filtered
  160 kV radiographs of a compact SiO₂/Cu/SAC305 package phantom.
- Reworked the gVXR Colab smoke test around an explicit deterministic Kramers
  spectrum after gVXR 2.1's automatic `setVoltage()` path returned an empty
  projection or crashed the current Colab runtime.
- Added Al/Cu filtering from gVXR mass attenuation coefficients, isolated
  renderer contexts for each spectrum, projection-shape validation, and Colab
  stale-notebook recovery guidance.

The original source is acknowledged at
<https://github.com/usnistgov/xsim-chip>.

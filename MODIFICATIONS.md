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

The original source is acknowledged at
<https://github.com/usnistgov/xsim-chip>.

# Final portfolio result

## Outcome

This portfolio extension is complete at the reproducible proof-of-concept
level. It turns the NIST `xsim-chip` workflow into a Colab-first semiconductor
package XCT demonstration with deterministic defect injection, GPU
reconstruction, defect metrology, root-cause screening hypotheses, tests, and
run manifests.

The project deliberately stops here. Full scanner calibration, a complete
multi-material gVXR package, and production defect-detection benchmarking are
documented future work rather than claims made by this repository.

## Verified result

| Item | Result |
| --- | --- |
| Runtime | Google Colab, Python 3.13.15 |
| GPU | NVIDIA Tesla T4, CUDA compute capability 7.5 |
| Reconstruction | ASTRA 2.5.0 `FBP_CUDA`, Hann filter |
| Synthetic volume | 129 × 129 × 129 voxels at 16 µm |
| Acquisition | 180 projections; detector 129 × 192 |
| Noise model | Poisson, 100,000 photons |
| Reconstruction time | 0.2337 s |
| Normalized RMSE | 0.244846 |
| Declared NumPy buffers | 0.0429 GiB |
| Controlled defect pixels | void 13; bridge 88; copper open 30 |
| Automated tests | 26 passing |

The normalized RMSE is a reproducible baseline, not an industrial acceptance
threshold. Attenuation values are relative, and the reduced reconstruction does
not model scatter, detector blur, or scanner calibration.

## Demonstrated workflow

1. Create deterministic semiconductor-package labels and controlled defects.
2. Generate noisy Beer–Lambert projections and reconstruct them on a Colab GPU.
3. Compare reference and candidate material volumes.
4. Group differences into three-dimensional defect components.
5. Report position, physical size, severity, and testable process hypotheses.
6. Save configuration, dependency, hardware, timing, and result metadata.

## Reproduce in Colab

- [Defect-analysis notebook](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/01_defect_analysis_colab.ipynb)
- [ASTRA GPU reconstruction notebook](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/02_astra_colab_gpu_smoke.ipynb)
- [Reduced gVXR spectral notebook](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/03_gvxr_colab_spectral.ipynb)
- [Archived ASTRA run record](results/colab_astra_smoke_2026-09-08.md)

## Resume-ready description

**Project:** Python-based X-ray CT defect inspection and root-cause analysis for
semiconductor packaging

- Extended NIST's open-source `xsim-chip` workflow into a reproducible Google
  Colab pipeline for synthetic package defects, X-ray projection, GPU CT
  reconstruction, and three-dimensional defect metrology.
- Implemented deterministic solder-void, solder-bridge, and copper-open test
  cases with material-aware connected-component analysis, severity ranking,
  physical measurements, and evidence-labelled root-cause hypotheses.
- Validated a 180-projection ASTRA CUDA/FBP workflow on an NVIDIA Tesla T4 in
  0.234 seconds with a recorded 0.244846 normalized RMSE and complete runtime
  manifest; added 26 automated tests and Python 3.11–3.13 CI coverage.

## Interview explanation

“I started from NIST's synthetic semiconductor-package CT project and focused
on making a smaller version reproducible in Colab. I added controlled defect
labels, GPU reconstruction, quantitative 3D defect reporting, and transparent
run metadata. The result is an engineering proof of concept rather than a
calibrated production inspection system, and the repository clearly separates
measured results from assumptions and future work.”

## Representative upstream images

Ground-truth synthetic package slice:

![Synthetic chip ground truth](../resources/simplified_chip_750p_Front_0376.jpg)

Reconstructed XCT slice with simulated artefacts:

![Reconstructed XCT slice](../resources/recon_2400_chip_4um_cone_Front_0376.jpg)

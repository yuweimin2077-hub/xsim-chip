# Colab ASTRA GPU smoke-test result — 2026-09-08

## Outcome

The reduced parallel-beam pipeline completed successfully in Google Colab on
a Tesla T4. ASTRA selected its CUDA implementation for both forward projection
and filtered backprojection, validating the notebook's intended GPU path.

## Reproducibility record

| Field | Recorded value |
| --- | --- |
| Source commit | `01780e2` |
| Colab Python | 3.13.15 |
| GPU | Tesla T4, 15360 MiB, CUDA compute capability 7.5 |
| ASTRA Toolbox | 2.5.0 |
| NumPy | 2.1.3 |
| SciPy | 1.16.3 |
| Profile | `quick-colab` |
| Volume shape | 129 × 129 × 129 |
| Detector shape | 129 × 192 |
| Projections | 180 |
| Voxel size | 16 µm |
| Random seed | 2060 |
| Reconstruction | `FBP_CUDA`, Hann filter |
| Photon count | 100,000 |
| Reconstruction time | 0.2337 s |
| Normalized RMSE | 0.244846 |
| Declared NumPy buffers | 0.0429 GiB |

Controlled defect masks contained 13 solder-void pixels, 88 solder-bridge
pixels, and 30 copper-open pixels in the deterministic 2D cross-section.

The notebook wrote the full run manifest plus reference labels, candidate
labels, noisy sinogram, and reconstruction arrays to `/content/xsim_outputs`.
These generated arrays are intentionally excluded from Git; rerunning
`notebooks/02_astra_colab_gpu_smoke.ipynb` recreates them.

## Interpretation

This result is a functional and reproducibility milestone, not a calibrated
image-quality benchmark. Attenuation is relative and the model does not yet
include scatter, detector blur, beam hardening, or a polychromatic spectrum.
The normalized RMSE is therefore recorded as a baseline for future simulation
improvements rather than as a production acceptance threshold.

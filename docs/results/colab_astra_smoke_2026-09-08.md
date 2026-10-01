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
| Actual reconstructed slice | 129 × 129 (2D) |
| Actual sinogram | 180 views × 192 detector bins |
| Planning-only 3D profile | 129 × 129 × 129; detector 129 × 192 |
| Projections | 180 |
| Voxel size | 16 µm |
| Random seed | 2060 |
| Reconstruction | `FBP_CUDA`, Hann filter |
| Photon count | 100,000 |
| Projection + noise + reconstruction stage time | 0.2337 s |
| Normalized RMSE | 0.244846 |
| Planning-only 3D declared NumPy buffers | 0.0429 GiB (not measured usage) |

Controlled defect masks contained 13 solder-void pixels, 88 solder-bridge
pixels, and 30 copper-open pixels in the deterministic 2D cross-section.

The notebook wrote the full run manifest plus reference labels, candidate
labels, noisy sinogram, and reconstruction arrays to `/content/xsim_outputs`.
These generated arrays are intentionally excluded from Git; rerunning
`notebooks/02_astra_colab_gpu_smoke.ipynb` recreates them.

## Interpretation

**Clarification added 2026-10-01:** the source notebook uses ASTRA `data2d`
and `FBP_CUDA`, so this validation reconstructed a 2D slice. The saved 129³
configuration described a planning estimate. The timer started before forward
projection; 0.2337 s is not isolated FBP time. The historical noise model did
not apply pixel-size attenuation scaling and normalized truth/reconstruction
by their separate maxima. These original measurements are retained, not
silently replaced with the new [closed-loop result](slice_closed_loop_2026-10-01.md).

This result is a functional and reproducibility milestone, not a calibrated
image-quality benchmark. Attenuation is relative and the model does not yet
include scatter, detector blur, beam hardening, or a polychromatic spectrum.
The normalized RMSE is therefore recorded as a baseline for future simulation
improvements rather than as a production acceptance threshold.

# 2D reconstruction to defect inspection result

> Historical 2D result. On 2026-10-02, [Notebook 04 connected the same CT
> functions to the 3D inspector](volume_bridge_2026-10-02.md) using 16 independent
> slice reconstructions. The measurements below are preserved unchanged.

## Completed chain

Known-good reference + injected candidate → 180 X-ray projections → noisy
FBP reconstruction → fixed-threshold material segmentation → aligned
reference comparison → suspected defect masks → independent truth evaluation.

This chain was executed on **2026-10-01 on local Windows**, both on an
**NVIDIA GeForce RTX 4060 Laptop GPU** and with forced CPU FBP. The code is
the same Python cells as the Colab notebook; only setup and output paths are
changed by the [local runner](../../tools/run_slice_notebook.py). These are
not new Colab T4 measurements. The updated
[Colab notebook](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/02_astra_colab_gpu_smoke.ipynb)
can reproduce the experiment on a T4.

![Reference, reconstruction, segmentation, and defect evaluation](slice_closed_loop_2026-10-01/overview.jpg)

## Configuration and measurements

| Setting or measurement | CUDA run | CPU fallback run |
| --- | --- | --- |
| ASTRA algorithm | `FBP_CUDA` | `FBP` |
| Phantom | 129 × 129 pixels, 16 µm/pixel | Same |
| Sinogram | 180 views × 192 detector bins | Same |
| Seed / photons / filter | 2060 / 100,000 / Hann | Same |
| Attenuation thresholds | 0.075 / 0.40 / 0.80 | Same |
| Minimum component | 4 pixels, 8-neighbour connectivity | Same |
| Full projection/noise/reconstruction stage | 0.051298 s | 0.021297 s |
| FBP run and result readback | 0.044829 s | 0.007441 s |
| Shared-scale NRMSE | 0.065717 | 0.065237 |
| Zero-photon rays | 0 | 0 |
| Suspected components / pixels | 6 / 216 | 6 / 212 |
| Union pixel precision | 0.467593 | 0.476415 |
| Union pixel recall | 0.770992 | 0.770992 |
| Union pixel Dice | 0.582133 | 0.588921 |
| Union pixel IoU | 0.410569 | 0.417355 |

Timings are individual wall-clock samples including initialization costs,
not a CPU/GPU speed comparison or isolated kernel benchmark. The 129³ profile
and 0.0429 GiB estimate in each manifest are **planning-only 3D settings**.
Actual acquisition is recorded separately under `experiment`.

The GPU run used Python 3.12.3, ASTRA 2.5.0, NumPy 2.5.3, and SciPy 1.18.1.
The fixed coefficients are synthetic relative per-mm values; multiplying by
0.016 mm before projection and dividing FBP output by that scale avoids the
old unit-pixel optical-depth saturation. NRMSE is
`sqrt(mean(((truth - reconstruction) / 0.95)**2))` with a shared known scale.
Neither coefficients nor thresholds are calibrated to a real scanner.

## CUDA defect evaluation

| Signature | Truth pixels | TP | FP | FN | Precision | Recall | Dice |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Missing solder / void | 13 | 13 | 111 | 0 | 0.104839 | 1.000000 | 0.189781 |
| Excess solder / bridge | 88 | 58 | 0 | 30 | 1.000000 | 0.659091 | 0.794521 |
| Missing copper / open | 30 | 30 | 4 | 0 | 0.882353 | 1.000000 | 0.937500 |
| Union | 131 | 101 | 115 | 30 | 0.467593 | 0.770992 | 0.582133 |

These are **strict 2D pixel-overlap metrics**, not object-level accuracy.
All three injected regions intersect predicted masks, but 30 bridge pixels
are missed. Hann smoothing and partial-volume boundaries cause 111 false
missing-solder pixels around the bumps. The six suspected components do not
mean that six true physical defects were injected. This baseline exposes
these errors rather than tuning its thresholds to the defect masks.

## Evidence and reproduction

- [CUDA runtime manifest](slice_closed_loop_2026-10-01/gpu_run_manifest.json)
- [CPU runtime manifest](slice_closed_loop_2026-10-01/cpu_run_manifest.json)
- [CUDA component report and scores](slice_closed_loop_2026-10-01/inspection_report.json)

```bash
python -m pip install -e ".[simulation]"
python tools/run_slice_notebook.py --output-dir outputs/slice_closed_loop_gpu
python tools/run_slice_notebook.py --cpu --output-dir outputs/slice_closed_loop_cpu
```

In Colab, run all notebook cells and retain `/content/xsim_outputs`.
Reconstruction, segmented labels, predicted masks, and truth masks are saved
there along with the report, manifest, and comparison image. Generated arrays
are intentionally outside Git.

At the time of this result, only the small **2D** loop was connected and the
**3D** inspection notebook used supplied material labels. The later
[slice-wise 3D result](volume_bridge_2026-10-02.md) now closes that data connection
and evaluates aggregate defect volume error. Real-data registration,
segmentation, calibrated metrology, and process-cause validation remain future work.

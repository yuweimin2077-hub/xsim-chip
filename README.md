# Semiconductor Package X-ray CT Inspection

A Colab-first portfolio extension of NIST's
[`xsim-chip`](https://github.com/usnistgov/xsim-chip) project for synthetic
semiconductor-package defects, GPU CT reconstruction, 3D defect metrology, and
root-cause screening hypotheses.

[![Tests](https://github.com/yuweimin2077-hub/xsim-chip/actions/workflows/tests.yml/badge.svg)](https://github.com/yuweimin2077-hub/xsim-chip/actions/workflows/tests.yml)
[![Defect analysis](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/01_defect_analysis_colab.ipynb)
[![ASTRA GPU](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/02_astra_colab_gpu_smoke.ipynb)
[![gVXR spectral](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/03_gvxr_colab_spectral.ipynb)

## What this project demonstrates

- Deterministic solder-void, solder-bridge, and copper-open defects.
- ASTRA forward projection and filtered backprojection on a Colab GPU.
- A complete 2D reconstruction-to-inspection baseline with fixed material
  thresholds, aligned reference comparison, and measured false positives/misses.
- Material-aware 3D connected-component inspection and physical measurements.
- Severity ranking with evidence-labelled root-cause hypotheses.
- Reproducibility manifests covering parameters, packages, hardware, and time.
- A reduced gVXR spectral smoke test with Al/Cu filtration.

## Verified results

| Item | Result |
| --- | --- |
| Current validation | Local NVIDIA RTX 4060 GPU and CPU fallback |
| Reconstructed slice | 129 × 129 pixels at 16 µm |
| Acquisition | 180 views × 192 detector bins |
| Reconstruction | ASTRA 2.5.0 `FBP_CUDA`, Hann filter |
| GPU projection + noise + reconstruction time | 0.051298 s |
| Shared-scale GPU normalized RMSE | 0.065717 |
| GPU pixel precision / recall / Dice | 0.468 / 0.771 / 0.582 |
| Current tests | 40 passing |

The [2D closed-loop result](docs/results/slice_closed_loop_2026-10-01.md)
includes configuration, errors, and runtime manifests; see the
[final portfolio summary](docs/FINAL_RESULT.md). The updated notebook is ready
for Colab. The [historical T4 run](docs/results/colab_astra_smoke_2026-09-08.md)
used an older attenuation/noise scale and RMSE normalization, so its results
are not directly comparable. The 129³ profile is a planning-only 3D estimate.

![2D reconstruction and defect comparison](docs/results/slice_closed_loop_2026-10-01/overview.jpg)

## Workflow

```text
synthetic package + controlled defects
                 ↓
       X-ray forward projection
                 ↓
          2D GPU reconstruction
                 ↓
  fixed material thresholds + aligned reference
                 ↓
2D defect masks → area → false positives and misses
```

3D labelled-volume inspection and process hypotheses are demonstrated
separately in the first notebook; reconstructed 3D CT inspection is future work.

## Run it

Open the **ASTRA GPU** badge above and run all cells for the complete 2D demo.
The defect-analysis notebook runs on CPU; ASTRA and gVXR are intended for a T4 GPU
runtime.

For a local rerun of the same experiment:

```bash
python -m pip install -e ".[simulation]"
python tools/run_slice_notebook.py
```

For supplied 3D labelled-volume inspection:

```bash
python -m pip install -e .
xsim-inspect reference.tif candidate.tif --output outputs/report.json
```

For development:

```bash
python -m pip install -e ".[dev]"
pytest
```

## Repository guide

| Path | Purpose |
| --- | --- |
| `xsim_chip_analysis/` | 2D/3D inspection, phantom, runtime, and spectral utilities |
| `notebooks/` | Three reproducible Colab demonstrations |
| `tests/` | Automated unit tests |
| `1_generate_chip_imgs/` | Original synthetic-package generation scripts |
| `2_xct_simulation/` | Original gVXR projection scripts |
| `3_xct_reconstruction/` | Original ASTRA reconstruction scripts |
| `docs/` | Results, assumptions, roadmap, and validation notes |

## Scope and limitations

This is a reproducible engineering proof of concept, not a calibrated
production inspection system. The reduced ASTRA experiment uses relative
attenuation and omits scatter, detector blur, and scanner calibration. The
gVXR notebook is intentionally a single-material smoke test. Root-cause outputs
are hypotheses for screening and require supporting process evidence.

The portfolio includes the small 2D closed loop; multi-material simulation and
production benchmarking remain future work in the [roadmap](docs/ROADMAP.md).

## Attribution

This derivative preserves the original NIST source and licensing notice.
Changes are documented in [MODIFICATIONS.md](MODIFICATIONS.md). NIST does not
endorse this derivative, and the software is provided without warranty. See
[LICENSE.md](LICENSE.md) for the full terms.

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
- Material-aware 3D connected-component inspection and physical measurements.
- Severity ranking with evidence-labelled root-cause hypotheses.
- Reproducibility manifests covering parameters, packages, hardware, and time.
- A reduced gVXR spectral smoke test with Al/Cu filtration.

## Verified Colab result

| Item | Result |
| --- | --- |
| GPU | NVIDIA Tesla T4 |
| Volume | 129 × 129 × 129 voxels at 16 µm |
| Acquisition | 180 projections; 129 × 192 detector |
| Reconstruction | ASTRA 2.5.0 `FBP_CUDA`, Hann filter |
| Reconstruction time | 0.2337 s |
| Normalized RMSE | 0.244846 |
| Tests | 26 passing |

See the [final portfolio result](docs/FINAL_RESULT.md) and
[archived Colab run](docs/results/colab_astra_smoke_2026-09-08.md) for the
complete configuration and interpretation.

![Reconstructed XCT slice](resources/recon_2400_chip_4um_cone_Front_0376.jpg)

## Workflow

```text
synthetic package + controlled defects
                 ↓
       X-ray forward projection
                 ↓
          GPU reconstruction
                 ↓
 reference/candidate volume comparison
                 ↓
3D defects → measurements → severity → hypotheses
```

## Run it

The fastest route is to open one of the Colab badges above. The defect-analysis
notebook runs on CPU; the ASTRA and gVXR notebooks are intended for a T4 GPU
runtime.

For local inspection:

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
| `xsim_chip_analysis/` | Inspection, phantom, runtime, and spectral utilities |
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

The portfolio scope is frozen after the completed Colab analytics and reduced
simulation milestones; more complex multi-material and production benchmarking
work is documented only as future work in the [roadmap](docs/ROADMAP.md).

## Attribution

This derivative preserves the original NIST source and licensing notice.
Changes are documented in [MODIFICATIONS.md](MODIFICATIONS.md). NIST does not
endorse this derivative, and the software is provided without warranty. See
[LICENSE.md](LICENSE.md) for the full terms.

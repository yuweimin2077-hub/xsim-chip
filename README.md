# Semiconductor Package X-ray CT Inspection

A Colab-first portfolio extension of NIST's
[`xsim-chip`](https://github.com/usnistgov/xsim-chip): synthetic package defects,
X-ray reconstruction, 3D defect measurements, and root-cause screening hypotheses.

**New — LLM + RAG inspection assistant:**
[![Open assistant in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/05_llm_rag_agent_colab.ipynb)

Ask a question in Chinese or English, inspect a registered reconstruction or
saved report, retrieve attributed technical notes, and produce a cited report.
Notebook 05 runs Qwen through PyTorch/Hugging Face with bounded tool calling.
Measurements stay in Python; the model selects relevant finding/source pairs,
and reviewed bilingual text supplies the explanations. See the
[assistant guide](docs/LLM_ASSISTANT.md) for scope and reproduction.
The [executed validation](docs/results/llm_assistant_2026-10-03.md) records real
Qwen CPU inference, three successful tool-workflow scenarios and 100 passing tests.

[![Tests](https://github.com/yuweimin2077-hub/xsim-chip/actions/workflows/tests.yml/badge.svg)](https://github.com/yuweimin2077-hub/xsim-chip/actions/workflows/tests.yml)

**Start here — connected 2D → 3D experiment:**
[![Open connected 3D demo in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/04_slice_wise_3d_colab.ipynb)

## What is connected

```text
3D package with depth-localized defects
→ parallel projections for every slice
→ shared 2D FBP reconstruction, repeated independently for 16 slices
→ reconstructed 3D volume → fixed material segmentation
→ existing 3D reference comparison → locations, volumes, and error metrics
```

The new notebook reuses the 2D reconstruction functions and the original 3D
inspector. Every layer uses its own projection data; no reconstructed slice
is copied to manufacture a volume. Defect truth is reserved for evaluation.

## Verified result

| Item | Local GPU result |
| --- | --- |
| Reconstructed volume `(z, y, x)` | 16 × 129 × 129 voxels; 16 µm spacing |
| Projections `(angle, z, bin)` | 180 × 16 × 192 |
| Reconstruction | ASTRA 2.5.0 `FBP_CUDA`, Hann filter |
| Shared-scale normalized RMSE | 0.064574 |
| Strict voxel precision / recall / Dice | 0.271 / 0.794 / 0.404 |
| CT validation | RTX 4060 Laptop GPU and CPU fallback |

The connection works, but simple thresholds still produce many boundary
false positives. This is **not production-grade defect detection**.
See the [full result and archived manifests](docs/results/volume_bridge_2026-10-02.md)
and [portfolio summary](docs/FINAL_RESULT.md). The updated Colab notebook uses
the same experiment code; this 3D result was measured locally, not on a Colab T4.

![Connected reconstruction and 3D inspection](docs/results/volume_bridge_2026-10-02/volume_connection.jpg)

## Run it

Open the Colab badge, choose a GPU runtime if available, and run all cells.
CPU fallback is supported. Outputs are saved in `/content/xsim_volume_outputs`.

```bash
python -m pip install -e ".[simulation]"
python tools/run_slice_notebook.py --volume
# Add --cpu to force CPU reconstruction.
```

| Notebook | Purpose |
| --- | --- |
| [05 · LLM + RAG assistant](notebooks/05_llm_rag_agent_colab.ipynb) | Cited report and bounded model-driven inspection tools |
| [04 · Connected 3D](notebooks/04_slice_wise_3d_colab.ipynb) | Recommended complete slice-wise experiment |
| [02 · Single-slice CT](notebooks/02_astra_colab_gpu_smoke.ipynb) | Smaller 2D reconstruction and inspection |
| [01 · 3D label inspection](notebooks/01_defect_analysis_colab.ipynb) | Standalone introduction to the same 3D inspector |
| [03 · gVXR spectral](notebooks/03_gvxr_colab_spectral.ipynb) | Separate single-material spectral smoke test |

Notebooks 01, 02, and 04 include saved local CPU/GPU outputs and inline figures:
open their GitHub preview to see results without running Colab.

For development: `python -m pip install -e ".[dev,simulation]"`, then `pytest`.
The original NIST generation, simulation, and reconstruction directories are
preserved. See the [Colab guide](docs/COLAB_GPU_WORKFLOW.md) for details.

For an offline, **retrieval-only** assistant report (no model download):

```bash
python -m xsim_chip_analysis.assistant.cli --report docs/results/volume_bridge_2026-10-02/volume_inspection_report.json
```

For actual model inference, install `.[llm]` and append
`--model Qwen/Qwen2.5-1.5B-Instruct --strict`. The model weights are downloaded
from Hugging Face on first use. Colab GPU and optional 4-bit loading are
documented in Notebook 05. This extension does not train or fine-tune a model.

## Scope and attribution

The bridge assumes aligned parallel-beam slices without cross-slice ray mixing.
It is not cone-beam reconstruction or calibrated industrial metrology. Relative
attenuation, synthetic alignment, and fixed thresholds omit real-scanner
effects. Root-cause entries are testable hypotheses, not proven diagnoses.
Further complexity is optional in the [roadmap](docs/ROADMAP.md).

This derivative preserves the original NIST source and [licensing notice](LICENSE.md).
NIST does not endorse this derivative; the software is provided without warranty.
Changes are listed in [MODIFICATIONS.md](MODIFICATIONS.md).

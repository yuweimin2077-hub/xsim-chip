# LLM inspection assistant: Colab T4 validation

**Passed on Google Colab with a Tesla T4 on 2026-10-03.** Notebook 05 and
three additional real-model cases completed in strict mode, without retrieval
fallback or rejected tool actions. This validates GPU execution and grounded
tool use on archived synthetic reports, not industrial detection accuracy.

## Measured environment

- Code commit: `efd65eba69ac40167dd21612b159a618280aa644`.
- Model: **Qwen/Qwen2.5-1.5B-Instruct**; `2.5` is the model generation and
  `1.5B` is the parameter size. This is not Qwen1.5.
- Model revision: `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- All model parameters on `cuda:0`, `torch.float16`; no CPU offload, 4-bit
  quantization, LoRA or SFT in this run.
- Tesla T4, 14.56 GiB available device memory; Python 3.13.15,
  PyTorch 2.11.0+cu130, CUDA 13.0, Transformers 4.57.6,
  Accelerate 1.15.0 and LM Format Enforcer 0.11.3.
- Peak PyTorch allocated memory across the three follow-up cases: **3.80 GiB**;
  peak reserved memory: **4.63 GiB**. These are allocator measurements, not
  whole-device memory use or model-loading peaks.

## Executed cases

| Case | Input | Workflow time | Accepted / rejected actions | Result |
| --- | --- | ---: | ---: | --- |
| Notebook default Chinese question | 3D, 82 difference components | 52.94 s | 3 / 0 | `llm_agent` |
| Chinese: voids and possible artifacts | 3D, 82 difference components | 80.24 s | 3 / 0 | `llm_agent` |
| English: can one slice establish a 3D volume fraction? | 2D, 6 difference components | 39.88 s | 3 / 0 | `llm_agent` |
| English: copper-open screening and missing evidence | 3D, 82 difference components | 38.98 s | 3 / 0 | `llm_agent` |

Every workflow executed `inspect_case -> search_knowledge -> finish` using
actual model inference. Times include the tool workflow but exclude dependency
installation and model download/loading. Follow-up timers synchronize CUDA
before and after each case. These are single observations, not throughput
benchmarks or a controlled CPU/GPU speed comparison.

Measurements match the source reports and the retrieval-only baseline exactly.
The 2D report retains square-micrometre units and the restriction against
claiming a 3D void fraction. The 82 3D differences are **not 82 confirmed defects**.
This run uses saved reports; it does not rerun or newly validate CT reconstruction
on Colab. The existing direct 3D comparison path remains available without
adding projection/reconstruction steps.

## Artifacts and reproduction

- [Executed Colab notebook](llm_colab_gpu_2026-10-03/executed_colab.ipynb),
  including installation logs, model metadata, GPU checks and original outputs.
- [Colab run screenshot](llm_colab_gpu_2026-10-03/colab_gpu_running.jpg), captured
  while the additional checks were running; final status is in the notebook and manifest.
- [GPU manifest](llm_colab_gpu_2026-10-03/gpu_validation.json) and
  [archive integrity checks](llm_colab_gpu_2026-10-03/archive_integrity.json).
- [Chinese report](llm_colab_gpu_2026-10-03/report.md),
  [English report](llm_colab_gpu_2026-10-03/report_en.md) and
  [default model/tool trace](llm_colab_gpu_2026-10-03/assistant_result.json).
- Additional raw traces: [voids](llm_colab_gpu_2026-10-03/volume_void.json),
  [single slice](llm_colab_gpu_2026-10-03/slice_area.json),
  [copper](llm_colab_gpu_2026-10-03/volume_copper.json).
- [Validation cells](llm_colab_gpu_2026-10-03/validation_cells.py): run after
  Notebook 05 in the same Colab namespace, with a loaded backend and result.

Open the executed notebook in Colab, save your own copy, choose a T4 runtime
and run all cells. Its first cell fetches GitHub `main`; for this exact source
snapshot, check out the code commit above before installing the package.
The model revision is pinned. Download both the notebook and result files
before ending the temporary runtime.

All 11 files in the runtime ZIP were compared byte-for-byte against the bundle
embedded in the saved notebook. Input hashes match the tested Git commit's
files. Windows checkout hashes can differ because Git converts LF to CRLF;
the normalized measurements are identical. The archived notebook corrects
inherited CPU provenance metadata and removes transient Colab cell metadata
and download-progress widget bindings. Model outputs and measurements are
retained. The original notebook and ZIP hashes are in the integrity manifest.
Notebook 05's regular source preview retains its separately labelled
[earlier CPU outputs](llm_assistant_2026-10-03.md).

## Limits observed

The small model sometimes selects the general artifact card for every selected
region. Valid source IDs and preserved measurements do not prove optimal
retrieval, complete explanations or manufacturing causal accuracy. The fixed
threshold CT detector still has substantial false positives. LoRA/SFT and
validation on independently reviewed real samples remain future work.

Colab installation emitted dependency conflicts for its preinstalled `diffusers`
and `gradio` packages because this project's Transformers 4.x stack installs
`huggingface-hub` 0.36.2. Neither package was used by this notebook, and all
model calls completed. Use a fresh runtime for this workflow; mixing it with
unrelated diffusion or UI notebooks was not validated. The public model ran
without a Hugging Face token.

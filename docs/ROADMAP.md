# Portfolio roadmap: semiconductor package XCT inspection

The objective is to turn the NIST proof of concept into a reproducible,
interview-ready engineering workflow while preserving upstream attribution.

> Portfolio scope is complete as of 2026-10-04: the reduced simulation and
> inspection workflows, the slice-wise 3D bridge, the evidence-grounded language
> assistant, and the synthetic LoRA pilot. The pilot includes a documented
> evidence-selection regression and remains experimental. The remaining
> unchecked items are optional future work, not release blockers.
> See the [final result](FINAL_RESULT.md) and [demo guide](DEMO_GUIDE.md).

## Milestone 1 — Colab-ready defect analytics

- [x] Preserve the NIST upstream history and licence.
- [x] Compare labelled reference and candidate volumes by material.
- [x] Locate 3D defect components and report physical measurements.
- [x] Rank severity and attach testable root-cause hypotheses.
- [x] Add unit tests and a Colab quick start.
- [x] Add a Python 3.11/3.12/3.13 GitHub Actions test workflow.
- [x] Publish the fork and verify GitHub Actions remotely.

## Milestone 2 — Reproducible simulation

- [x] Add explicit phantom size, random seed, projection count, and detector profiles.
- [x] Add a low-memory Colab profile and ASTRA CUDA capability check.
- [x] Record run configuration, dependency versions, duration, platform, and GPU.
- [x] Quantify major host-memory buffers for quick and NIST-reference profiles.
- [x] Implement and locally validate the reduced parallel-beam experiment inputs.
- [x] Run and archive the ASTRA forward/reconstruction result in Colab.
- [x] Integrate and validate a reduced single-material gVXR spectral projection
  after the ASTRA smoke test.
- [x] Connect the reconstructed 2D slice to fixed-threshold material segmentation,
  aligned reference comparison, defect masks, and strict pixel-level metrics.
- [x] Verify the same notebook Python cells locally on CUDA and CPU; archive
  manifests, inspection report, and a six-panel figure.
- [x] Correct dimensionality and timing claims in the historical T4 result.
- [x] Connect independent 2D slice reconstructions into a 16-layer volume and
  pass its segmented labels to the existing 3D inspector (Notebook 04).
- [x] Execute the full bridge locally on CUDA and CPU and archive the results.
- [ ] Extend the gVXR projection to the SiO₂/Cu/SAC305 package phantom.
- [ ] Validate a reduced 3D cone-beam reconstruction and measure peak VRAM.

## Milestone 3 — Realistic defect injection

- [x] Add depth-localized solder void, bridge, and copper open test cases.
- [x] Produce paired 3D ground-truth masks for independent evaluation.
- [ ] Add missing bump and layer misalignment generators.
- [ ] Define broader defect size, location, and prevalence experiment matrices.

## Milestone 4 — Detection and metrology

- [x] Segment a reconstructed 2D slice and measure strict pixel precision,
  recall, Dice, IoU, and suspected component area without truth-fitted thresholds.
- [x] Segment a slice-wise reconstructed volume with fixed thresholds and
  report 3D positions, bounding boxes, and candidate-region volumes.
- [x] Measure strict voxel precision, recall, Dice/IoU, and aggregate signature
  volume error, retaining false positives and misses.
- [ ] Validate object-matched localisation and metrology accuracy.
- [ ] Compare robustness across noise, artefact, and projection-count conditions.

## Milestone 5 — Root-cause analysis and presentation

- [ ] Join defect signatures with simulated process parameters.
- [ ] Add interpretable feature importance and hypothesis calibration.
- [x] Publish a concise portfolio summary, figures, measured error tables,
  and a reproducible connected demo.
- [ ] Add a bilingual presentation and process-parameter benchmark study.

## Milestone 6 — Evidence-grounded language assistant

- [x] Wrap saved 2D/3D reports and live reconstructed-array inspection as tools.
- [x] Add a bilingual, attributed starter corpus with BM25 retrieval.
- [x] Add optional PyTorch/Hugging Face model inference and bounded JSON tool actions.
- [x] Validate source/finding references and preserve numeric measurements in Python.
- [x] Add a Colab notebook, offline baseline, command-line interface and regression tests.
- [x] Execute the real model on Colab T4; archive CUDA/FP16 evidence, three
  follow-up scenarios, memory/timing measurements and the executed notebook.
- [ ] Train and evaluate LoRA/SFT adapters on independently reviewed cases.
- [x] Complete a separate synthetic workflow LoRA pilot on Colab T4; archive
  adapter weights, held-out comparisons and the evidence-selection regression.
- [ ] Extend and evaluate the knowledge corpus with domain experts and real samples.

## Engineering rules

- Every result must be reproducible from a notebook or command.
- Root-cause outputs are hypotheses, never unsupported diagnoses.
- Large generated data stays outside Git; small fixtures remain deterministic.
- Upstream changes are fetched from `upstream/main` and merged deliberately.

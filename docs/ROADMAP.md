# Portfolio roadmap: semiconductor package XCT inspection

The objective is to turn the NIST proof of concept into a reproducible,
interview-ready engineering workflow while preserving upstream attribution.

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
- [ ] Integrate reduced gVXR spectral projection after the ASTRA smoke test.
- [ ] Validate a reduced 3D cone-beam reconstruction and measure peak VRAM.

## Milestone 3 — Realistic defect injection

- Add controlled solder void, bridge, missing bump, copper open, and layer
  misalignment generators.
- Produce paired ground-truth masks for detection evaluation.
- Define defect size, location, and prevalence experiment matrices.

## Milestone 4 — Detection and metrology

- Segment reconstructed volumes with a documented baseline.
- Measure precision, recall, Dice/IoU, defect volume error, and localisation
  error against synthetic ground truth.
- Compare robustness across noise, artefact, and projection-count conditions.

## Milestone 5 — Root-cause analysis and presentation

- Join defect signatures with simulated process parameters.
- Add interpretable feature importance and hypothesis calibration.
- Publish a bilingual technical report, figures, benchmark table, and a short
  demo suitable for an Applied Materials interview.

## Engineering rules

- Every result must be reproducible from a notebook or command.
- Root-cause outputs are hypotheses, never unsupported diagnoses.
- Large generated data stays outside Git; small fixtures remain deterministic.
- Upstream changes are fetched from `upstream/main` and merged deliberately.

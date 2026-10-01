# Colab GPU workflow

## Why a reduced profile is required

The NIST parallel-beam script allocates a 2400 × 1001 × 1201 float32
projection stack and a same-sized uint16 buffer. Together those two arrays are
about 16.1 GiB before reconstruction, mesh storage, Python overhead, or
gVXR/ASTRA internal allocations. The transparent estimator in
`xsim_chip_analysis.runtime` reports about 19.67 GiB for the major declared
host-side arrays.

The `quick-colab` planning profile describes a 129³ labelled volume, 180
projections, and a 129 × 192 detector, with about 0.043 GiB of declared buffers.
The executed notebook instead reconstructs a **129 × 129 2D slice** from a
**180 × 192 sinogram**. The 3D estimates are clearly labelled planning-only;
they are not actual 3D reconstruction dimensions or measured memory usage.

## Notebook sequence

1. Open `notebooks/02_astra_colab_gpu_smoke.ipynb` in Colab.
2. Select a T4 GPU runtime when available.
3. Run the dependency and capability cells.
4. Compare the printed quick and NIST-reference memory estimates.
5. Generate deterministic reference and defect-injected package slices.
6. Run parallel-beam forward projection and Hann-filtered FBP.
7. Segment the reconstructed attenuation with fixed material thresholds.
8. Compare to the aligned reference; inspect the six-panel result and strict
   pixel precision/recall/Dice, including false positives and missed pixels.
9. Download `/content/xsim_outputs` to retain the report, figure, labels,
   predicted/truth masks, sinogram, reconstruction, and run manifest.

The first archived T4 validation is recorded in
[`results/colab_astra_smoke_2026-09-08.md`](results/colab_astra_smoke_2026-09-08.md).
The completed 2D chain was also executed locally on GPU and CPU; see the
[2026-10-01 result](results/slice_closed_loop_2026-10-01.md). This is not a
new Colab T4 validation; run the updated notebook to record a T4 result.

The `xsim-chip-analysis` package supports Python 3.11–3.14 so that it can run
on current Colab runtimes. The upstream precompiled `img2stl` Cython extension
is a separate constraint and remains limited to its supplied Python 3.11/3.12
binaries; this smoke test does not import that extension.

The notebook follows ASTRA's documented `create_projector`, `create_sino`,
`FBP_CUDA`, `use_cuda`, and `get_gpu_info` interfaces. See the official
[installation guide](https://astra-toolbox.com/docs/install.html),
[FBP_CUDA example](https://astra-toolbox.com/docs/algs/FBP_CUDA.html), and
[GPU/runtime guidance](https://astra-toolbox.com/docs/misc.html).

## Interpretation limits

- Material coefficients are relative attenuation values for pipeline
  validation; they are not calibrated mass attenuation coefficients.
- The unit-pixel projector receives relative per-mm attenuation multiplied by
  0.016 mm; FBP output is divided by that factor before fixed-threshold
  segmentation. Thresholds are 0.075, 0.40, 0.80 and are not fit to defect truth.
- Reference and candidate share synthetic coordinates. No real-data
  registration is validated. Minimum component size is four pixels with
  eight-neighbour connectivity; areas are µm² rather than 3D volumes.
- Shared known attenuation normalization and explicit FBP/stage timers replace
  the old normalization/timing conventions, so historical results are not
  directly comparable. FBP timing includes result readback.
- Poisson noise is included, but detector blur, scatter, beam hardening, and a
  polychromatic spectrum are not yet modelled.
- Reduced single-material gVXR validation is a separate notebook; 3D cone-beam
  reconstruction remains optional future work.

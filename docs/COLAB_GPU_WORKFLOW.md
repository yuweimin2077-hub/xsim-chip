# Colab GPU workflow

## Why a reduced profile is required

The NIST parallel-beam script allocates a 2400 × 1001 × 1201 float32
projection stack and a same-sized uint16 buffer. Together those two arrays are
about 16.1 GiB before reconstruction, mesh storage, Python overhead, or
gVXR/ASTRA internal allocations. The transparent estimator in
`xsim_chip_analysis.runtime` reports about 19.67 GiB for the major declared
host-side arrays.

The `quick-colab` profile uses a 129³ labelled volume, 180 projections, and a
129 × 192 detector. Its corresponding declared buffers are about 0.043 GiB.
This profile is a functional smoke test, not a claim of production-equivalent
image quality.

## Notebook sequence

1. Open `notebooks/02_astra_colab_gpu_smoke.ipynb` in Colab.
2. Select a T4 GPU runtime when available.
3. Run the dependency and capability cells.
4. Compare the printed quick and NIST-reference memory estimates.
5. Generate deterministic reference and defect-injected package slices.
6. Run parallel-beam forward projection and Hann-filtered FBP.
7. Inspect the sinogram, reconstruction, error map, NRMSE, and run manifest.
8. Download `/content/xsim_outputs` if the experiment should be retained.

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
- Poisson noise is included, but detector blur, scatter, beam hardening, and a
  polychromatic spectrum are not yet modelled.
- gVXR spectral simulation and reduced 3D cone-beam reconstruction are the next
  validation steps.

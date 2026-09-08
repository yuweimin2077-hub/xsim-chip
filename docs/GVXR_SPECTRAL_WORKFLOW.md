# Reduced gVXR spectral workflow

`notebooks/03_gvxr_colab_spectral.ipynb` advances the project from a relative,
monoenergetic ASTRA smoke test to material- and energy-dependent gVXR
radiography. It is deliberately compact enough for a standard Colab T4.

## Modelled experiment

- 160 kV cone-beam point source represented by a deterministic Kramers-law
  continuum with 4 keV energy bins and a 1 mAs scaling assumption.
- An unfiltered reference exposure followed by 0.5 mm Al inherent filtration
  and an additional 1.0 mm Cu filter.
- A 192 × 128 ideal energy-integrating detector with 0.16 mm detector pixels.
- A magnification of 3 and an object-plane pixel size of about 53.3 µm.
- A deterministic single SiO₂ cuboid smoke-test phantom; multi-material
  package geometry is tracked as a follow-up because it currently destabilises
  the Colab gVXR 2.1 runtime.
- A gVXR 2.1 `createOpenGLContext` renderer. Energy bins are loaded explicitly
  before detector creation because the automatic `setVoltage()` projection
  path returns an empty buffer or crashes the current Colab runtime.

The notebook compares the two spectra, records mean/peak energy and the
low-energy photon fraction, computes flat-field-normalised transmission, and
quantifies the filtered/unfiltered difference. The full configuration,
environment, versions, elapsed time, spectrum summaries, and result metrics
are written to `/content/xsim_outputs/gvxr_spectral/run_manifest.json`.

## Why this is separate from the ASTRA notebook

gVXR uses GPU-accelerated polygon rendering and energy-dependent Beer–Lambert
attenuation to generate radiographs. ASTRA consumes projection data to perform
tomographic reconstruction. Keeping the spectral radiography validation
separate makes failures and assumptions easier to isolate before the two tools
are joined in a reduced 3D cone-beam CT experiment.

## Interpretation limits

- This stage uses one built-in cuboid instead of the thousands of STL
  components in the full upstream phantom.
- The notebook rejects empty or incorrectly sized gVXR projection buffers
  before normalisation and explains how to recover from a cached legacy tab.
- The Kramers continuum is a deterministic compatibility smoke test, not a
  calibrated tungsten-target tube spectrum. Filter attenuation uses gVXR's
  tabulated mass attenuation coefficients and nominal Al/Cu densities.
- Geometry, tube voltage, filtration, and exposure are documented simulation
  assumptions, not parameters calibrated to a specific commercial scanner.
- The detector is ideal and energy integrating; scatter, detector blur,
  electronic noise, and focal-spot blur are not yet included.
- gVXR is based on Beer–Lambert attenuation and is intended for cases where
  photon scattering is negligible.

The implementation follows the official gVXR
[installation guide](https://gvirtualxray.sourceforge.io/install/),
[feature description](https://gvirtualxray.sourceforge.io/), and
[polychromatism tutorial](https://github.com/TomographicImaging/gVXR-Tutorials/blob/main/notebooks/polychromatism.ipynb).

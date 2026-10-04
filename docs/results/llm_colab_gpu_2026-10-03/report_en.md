# CT defect screening report

Mode: `llm_agent`

Measurements come from the inspection tool. The model selects finding/source links; explanations come from reviewed source cards.

## Measured screening facts

- 3D; shape: [16, 129, 129]; spacing: 16.0 um.
- Candidate provenance: `fixed_threshold_segmentation_of_reconstructed_slice_stack`.
- 82 material-difference components; this is not a count of confirmed defects.

| ID | Screening signature | Size | Centroid (um) |
| --- | --- | --- | --- |
| D0001 | copper_bridge_or_residue | 8126464.000 um3 | (122.153, 1471.887, 1245.613) |
| D0002 | copper_bridge_or_residue | 3784704.000 um3 | (119.775, 1471.758, 576.727) |
| D0003 | solder_void_or_open | 2478080.000 um3 | (119.802, 1471.524, 577.269) |
| D0004 | solder_void_or_open | 2375680.000 um3 | (116.386, 1471.503, 1019.366) |
| D0005 | solder_void_or_open | 2351104.000 um3 | (116.739, 1471.666, 1476.181) |
| D0006 | solder_bridge | 1425408.000 um3 | (168.000, 1480.276, 1248.000) |
| D0007 | copper_open_or_underfill | 1089536.000 um3 | (87.940, 577.023, 1016.662) |
| D0008 | solder_void_or_open | 692224.000 um3 | (120.331, 1472.284, 1024.000) |
| D0009 | dielectric_void_or_crack | 3190784.000 um3 | (152.154, 1476.929, 1248.144) |
| D0010 | dielectric_misalignment | 1089536.000 um3 | (87.940, 577.023, 1016.662) |
| D0011 | copper_bridge_or_residue | 397312.000 um3 | (120.577, 1472.495, 1024.000) |
| D0012 | dielectric_misalignment | 266240.000 um3 | (120.615, 1472.000, 1024.000) |
| D0013 | dielectric_void_or_crack | 196608.000 um3 | (120.000, 1392.000, 496.000) |
| D0014 | dielectric_void_or_crack | 196608.000 um3 | (120.000, 1392.000, 944.000) |
| D0015 | dielectric_void_or_crack | 196608.000 um3 | (120.000, 1392.000, 1552.000) |
| D0016 | dielectric_void_or_crack | 196608.000 um3 | (120.000, 1552.000, 496.000) |
| D0017 | dielectric_void_or_crack | 196608.000 um3 | (120.000, 1552.000, 656.000) |
| D0018 | dielectric_void_or_crack | 196608.000 um3 | (120.000, 1552.000, 944.000) |
| D0019 | dielectric_void_or_crack | 196608.000 um3 | (120.000, 1552.000, 1552.000) |
| D0020 | dielectric_void_or_crack | 192512.000 um3 | (118.128, 1391.660, 655.660) |
| D0021 | dielectric_void_or_crack | 94208.000 um3 | (125.217, 1360.000, 1003.130) |
| D0022 | dielectric_void_or_crack | 73728.000 um3 | (121.778, 1360.000, 1041.778) |
| D0023 | dielectric_void_or_crack | 73728.000 um3 | (127.111, 1584.000, 1006.222) |
| D0024 | dielectric_void_or_crack | 69632.000 um3 | (114.824, 1455.059, 912.000) |
| D0025 | dielectric_void_or_crack | 69632.000 um3 | (113.882, 1455.059, 1584.000) |
| D0026 | dielectric_void_or_crack | 69632.000 um3 | (113.882, 1488.941, 912.000) |
| D0027 | dielectric_void_or_crack | 69632.000 um3 | (114.824, 1584.000, 1040.941) |
| D0028 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 352.000) |
| D0029 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 416.000) |
| D0030 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 800.000) |
| D0031 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 1008.000) |
| D0032 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 1072.000) |
| D0033 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 1184.000) |
| D0034 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 1248.000) |
| D0035 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 1472.000) |
| D0036 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1040.000, 1632.000) |
| D0037 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1360.000, 560.000) |
| D0038 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1360.000, 592.000) |
| D0039 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1360.000, 1456.000) |
| D0040 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1360.000, 1488.000) |
| D0041 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1456.000, 464.000) |
| D0042 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1456.000, 688.000) |
| D0043 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1488.000, 464.000) |
| D0044 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1488.000, 688.000) |
| D0045 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1488.000, 1584.000) |
| D0046 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1584.000, 560.000) |
| D0047 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1584.000, 592.000) |
| D0048 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1584.000, 1456.000) |
| D0049 | dielectric_void_or_crack | 65536.000 um3 | (120.000, 1584.000, 1488.000) |
| D0050 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 352.000) |
| D0051 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 416.000) |
| D0052 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 800.000) |
| D0053 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 1008.000) |
| D0054 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 1072.000) |
| D0055 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 1184.000) |
| D0056 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 1248.000) |
| D0057 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 1472.000) |
| D0058 | copper_bridge_or_residue | 65536.000 um3 | (120.000, 1040.000, 1632.000) |
| D0059 | dielectric_void_or_crack | 61440.000 um3 | (128.000, 1712.000, 160.000) |
| D0060 | dielectric_void_or_crack | 53248.000 um3 | (96.000, 1040.000, 592.000) |
| D0061 | dielectric_void_or_crack | 53248.000 um3 | (144.000, 784.000, 1248.000) |
| D0062 | dielectric_void_or_crack | 53248.000 um3 | (144.000, 1040.000, 864.000) |
| D0063 | copper_bridge_or_residue | 53248.000 um3 | (96.000, 1040.000, 592.000) |
| D0064 | copper_bridge_or_residue | 53248.000 um3 | (144.000, 784.000, 1248.000) |
| D0065 | copper_bridge_or_residue | 53248.000 um3 | (144.000, 1040.000, 864.000) |
| D0066 | dielectric_void_or_crack | 49152.000 um3 | (152.000, 608.000, 800.000) |
| D0067 | copper_bridge_or_residue | 49152.000 um3 | (152.000, 608.000, 800.000) |
| D0068 | dielectric_void_or_crack | 40960.000 um3 | (72.000, 848.000, 1248.000) |
| D0069 | copper_bridge_or_residue | 40960.000 um3 | (72.000, 848.000, 1248.000) |
| D0070 | dielectric_void_or_crack | 36864.000 um3 | (64.000, 784.000, 800.000) |
| D0071 | dielectric_void_or_crack | 36864.000 um3 | (64.000, 848.000, 1072.000) |
| D0072 | dielectric_void_or_crack | 36864.000 um3 | (128.000, 848.000, 592.000) |
| D0073 | dielectric_misalignment | 36864.000 um3 | (176.000, 1088.000, 1840.000) |
| D0074 | copper_open_or_underfill | 36864.000 um3 | (176.000, 1088.000, 1840.000) |
| D0075 | copper_bridge_or_residue | 36864.000 um3 | (64.000, 784.000, 800.000) |
| D0076 | copper_bridge_or_residue | 36864.000 um3 | (64.000, 848.000, 1072.000) |
| D0077 | copper_bridge_or_residue | 36864.000 um3 | (128.000, 848.000, 592.000) |
| D0078 | dielectric_void_or_crack | 32768.000 um3 | (56.000, 1040.000, 1696.000) |
| D0079 | dielectric_void_or_crack | 32768.000 um3 | (184.000, 784.000, 1008.000) |
| D0080 | dielectric_void_or_crack | 32768.000 um3 | (184.000, 1712.000, 1872.000) |
| D0081 | copper_bridge_or_residue | 32768.000 um3 | (56.000, 1040.000, 1696.000) |
| D0082 | copper_bridge_or_residue | 32768.000 um3 | (184.000, 784.000, 1008.000) |

Coordinate order: z, y, x

## Candidate interpretations and checks

Interpretations cover selected representative regions, not an individual review of every component.

- **D0001** — The project assigns copper-difference signatures by comparing material labels. These labels do not measure electrical continuity or establish a plating or etching cause. [K-COPPER](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/inspection.py)
  Review reconstruction and segmentation, then use continuity tests or process records when a physical cause must be established.
- **D0009, D0007, D0010** — The archived slice-wise experiment shows boundary misclassification after Hann FBP and fixed thresholding, including missing-solder predictions on clean slices. Candidate differences are not confirmed physical defects. [K-ARTIFACT](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md)
  Inspect grayscale, reference alignment and neighboring slices together; validate any revised segmentation on independent samples.
- **D0003** — TI describes how reflow flux activity and thermal-via treatment can affect QFN/SON voiding. This is background for a candidate explanation, not proof of the cause in this synthetic sample. [K-VOID](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=7)
  If applicable to the actual package, review the paste supplier's reflow profile and via design; compare adjacent slices before confirming a void.
- **D0006** — TI relates solder-bridge prevention to pad geometry and clearance. Excess-solder differences are a screening signature; imaging errors can also produce them. [K-BRIDGE](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=6)
  Review the actual land pattern and confirm connectivity in the reconstructed region. Do not import a package-specific acceptance limit into this demo.

## Evidence limits

- Fixed thresholds and imaging artifacts can cause false positives or misses; review grayscale data and adjacent slices.
- No manufacturing root cause, calibrated confidence probability or industrial pass/fail disposition is established.
- No joint void-volume fraction is calculated: a segmented joint denominator is required; 2D area is not 3D volume.

## Sources

- [K-COPPER: Copper differences require independent confirmation](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/inspection.py) — _DEFECT_KINDS and analyze_against_reference. Project screening logic, not externally validated causal evidence.
- [K-VOID: QFN/SON voiding: reflow and via design](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=7) — SLUA271C, December 2023, section 3.4.1, printed page 7. QFN/SON assembly guidance; applicability to other package geometries requires review.
- [K-BRIDGE: QFN/SON solder bridging and land geometry](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=6) — SLUA271C, December 2023, sections 3.2-3.4, printed pages 6-7. QFN/SON geometry guidance; no universal pass/fail rule.
- [K-ARTIFACT: Measured boundary false positives in the synthetic CT baseline](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md) — Measured result and CUDA per-signature evaluation. Project synthetic baseline; not a general scanner calibration.

# CT 缺陷筛查报告

模式: `llm_agent`

本报告中的数值来自检测工具。模型选择资料与区域的对应关系，解释文字来自经过审核的资料卡。

## 检测事实

- 2D; shape: [129, 129]; spacing: 16.0 um.
- Candidate provenance: `segmented_reconstructed_slice`.
- 共 6 个材料差异连通域；这不是已确认缺陷的数量。

| 编号 | 筛查信号 | 大小 | 中心坐标 (um) |
| --- | --- | --- | --- |
| S0001 | 疑似焊料缺失 | 9984.000 um2 | (1472.000, 578.462) |
| S0002 | 疑似焊料缺失 | 8192.000 um2 | (1469.000, 1008.500) |
| S0003 | 疑似焊料缺失 | 8192.000 um2 | (1475.000, 1487.500) |
| S0004 | 疑似焊料缺失 | 5376.000 um2 | (1472.000, 1024.000) |
| S0005 | 疑似多余焊料/桥连 | 14848.000 um2 | (1480.276, 1248.000) |
| S0006 | 疑似铜缺失 | 8704.000 um2 | (577.412, 1018.824) |

坐标顺序：y, x

## 候选解释与复核

解释只覆盖选出的代表性区域，不代表已逐一复核全部连通域。

- **S0005, S0001, S0006, S0002, S0003, S0004** — 已归档的逐层实验显示，Hann FBP 与固定阈值分割会导致边界误分，包括在无缺陷层中预测出焊料缺失。候选差异不等于已确认的物理缺陷。 [K-ARTIFACT](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md)
  同时检查灰度图、参考体对齐情况和相邻切片；改进分割后，用独立样本验证。

## 需要保留的限制

- 固定阈值与成像伪影可能造成误报或漏检；请复核原始灰度图及相邻切片。
- 未确认制造根因，没有校准后的置信概率或工业合格判定。
- 未计算焊点体积占比：需要明确的焊点分割与分母；二维面积不能换称三维体积。

## 资料来源

- [K-2D: A slice measures area, not defect volume](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/slice_inspection.py) — inspect_reconstructed_slice. Dimensionality and denominator constraints.
- [K-GEOMETRY: Slice-wise 3D geometry and measurements](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/parallel_beam.py) — reconstruct_projection_stack. Aligned synthetic slice-wise parallel-beam model.
- [K-ARTIFACT: Measured boundary false positives in the synthetic CT baseline](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md) — Measured result and CUDA per-signature evaluation. Project synthetic baseline; not a general scanner calibration.
- [K-VOID: QFN/SON voiding: reflow and via design](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=7) — SLUA271C, December 2023, section 3.4.1, printed page 7. QFN/SON assembly guidance; applicability to other package geometries requires review.

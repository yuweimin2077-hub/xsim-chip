# CT 缺陷筛查报告

模式: `llm_agent`

本报告中的数值来自检测工具。模型选择资料与区域的对应关系，解释文字来自经过审核的资料卡。

## 检测事实

- 2D; shape: [34, 29]; spacing: 8.0 um.
- Candidate provenance: `segmented_reconstructed_slice`.
- 共 0 个材料差异连通域；这不是已确认缺陷的数量。

| 编号 | 筛查信号 | 大小 | 中心坐标 (um) |
| --- | --- | --- | --- |

坐标顺序：y, x

## 候选解释与复核

解释只覆盖选出的代表性区域，不代表已逐一复核全部连通域。

没有可支持的区域解释；未检出差异不能证明无缺陷。

## 需要保留的限制

- 固定阈值与成像伪影可能造成误报或漏检；请复核原始灰度图及相邻切片。
- 未确认制造根因，没有校准后的置信概率或工业合格判定。
- 未计算焊点体积占比：需要明确的焊点分割与分母；二维面积不能换称三维体积。

## 资料来源

- [K-SCOPE: Evidence limits and root-cause hypotheses](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/FINAL_RESULT.md) — Scope and limitations of the completed synthetic integration. Project limitations; no industrial acceptance certification.
- [K-2D: A slice measures area, not defect volume](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/slice_inspection.py) — inspect_reconstructed_slice. Dimensionality and denominator constraints.
- [K-GEOMETRY: Slice-wise 3D geometry and measurements](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/parallel_beam.py) — reconstruct_projection_stack. Aligned synthetic slice-wise parallel-beam model.
- [K-COPPER: Copper differences require independent confirmation](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/inspection.py) — _DEFECT_KINDS and analyze_against_reference. Project screening logic, not externally validated causal evidence.


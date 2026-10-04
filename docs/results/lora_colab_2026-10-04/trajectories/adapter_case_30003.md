# CT 缺陷筛查报告

模式: `llm_agent`

本报告中的数值来自检测工具。模型选择资料与区域的对应关系，解释文字来自经过审核的资料卡。

## 检测事实

- 3D; shape: [26, 34, 32]; spacing: 8.0 um.
- Candidate provenance: `supplied_material_labels`.
- 共 1 个材料差异连通域；这不是已确认缺陷的数量。

| 编号 | 筛查信号 | 大小 | 中心坐标 (um) |
| --- | --- | --- | --- |
| F30003_1 | 疑似多余焊料/桥连 | 13824.000 um3 | (32.000, 32.000, 144.000) |

坐标顺序：z, y, x

## 候选解释与复核

解释只覆盖选出的代表性区域，不代表已逐一复核全部连通域。

- **F30003_1** — 已归档的逐层实验显示，Hann FBP 与固定阈值分割会导致边界误分，包括在无缺陷层中预测出焊料缺失。候选差异不等于已确认的物理缺陷。 [K-ARTIFACT](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md)
  同时检查灰度图、参考体对齐情况和相邻切片；改进分割后，用独立样本验证。
- **F30003_1** — 差异及规则严重程度属于筛查结果。目前没有提供工艺测量或校准后的因果概率；未检出差异也不能证明器件无缺陷。 [K-SCOPE](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/FINAL_RESULT.md)
  作制造处置前，需要工艺记录、独立检测和适用的验收标准。
- **F30003_1** — TI 将焊桥预防与焊盘几何及间距联系起来。多余焊料差异属于筛查信号，成像误差也可能产生这种信号。 [K-BRIDGE](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=6)
  检查实际焊盘布局并复核重建区域的连通性，不把特定封装的验收限值直接套用到本演示。

## 需要保留的限制

- 固定阈值与成像伪影可能造成误报或漏检；请复核原始灰度图及相邻切片。
- 未确认制造根因，没有校准后的置信概率或工业合格判定。
- 未计算焊点体积占比：需要明确的焊点分割与分母；二维面积不能换称三维体积。

## 资料来源

- [K-BRIDGE: QFN/SON solder bridging and land geometry](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=6) — SLUA271C, December 2023, sections 3.2-3.4, printed pages 6-7. QFN/SON geometry guidance; no universal pass/fail rule.
- [K-SCOPE: Evidence limits and root-cause hypotheses](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/FINAL_RESULT.md) — Scope and limitations of the completed synthetic integration. Project limitations; no industrial acceptance certification.
- [K-COPPER: Copper differences require independent confirmation](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/inspection.py) — _DEFECT_KINDS and analyze_against_reference. Project screening logic, not externally validated causal evidence.
- [K-ARTIFACT: Measured boundary false positives in the synthetic CT baseline](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md) — Measured result and CUDA per-signature evaluation. Project synthetic baseline; not a general scanner calibration.


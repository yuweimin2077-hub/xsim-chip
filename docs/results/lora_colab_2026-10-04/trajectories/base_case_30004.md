# CT 缺陷筛查报告

模式: `llm_agent`

本报告中的数值来自检测工具。模型选择资料与区域的对应关系，解释文字来自经过审核的资料卡。

## 检测事实

- 2D; shape: [27, 27]; spacing: 4.0 um.
- Candidate provenance: `segmented_reconstructed_slice`.
- 共 2 个材料差异连通域；这不是已确认缺陷的数量。

| 编号 | 筛查信号 | 大小 | 中心坐标 (um) |
| --- | --- | --- | --- |
| F30004_1 | 疑似焊料缺失 | 256.000 um2 | (30.000, 30.000) |
| F30004_2 | 疑似铜缺失 | 64.000 um2 | (74.000, 74.000) |

坐标顺序：y, x

## 候选解释与复核

解释只覆盖选出的代表性区域，不代表已逐一复核全部连通域。

- **F30004_1** — TI 指出，回流过程中的助焊剂活性和散热过孔处理会影响 QFN/SON 空洞。这只能提供候选解释，不能证明本合成样本的制造根因。 [K-VOID](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=7)
  若实际封装适用，检查焊膏供应商的回流曲线和过孔设计，并结合相邻切片复核空洞。
- **F30004_2** — 已归档的逐层实验显示，Hann FBP 与固定阈值分割会导致边界误分，包括在无缺陷层中预测出焊料缺失。候选差异不等于已确认的物理缺陷。 [K-ARTIFACT](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md)
  同时检查灰度图、参考体对齐情况和相邻切片；改进分割后，用独立样本验证。

## 需要保留的限制

- 固定阈值与成像伪影可能造成误报或漏检；请复核原始灰度图及相邻切片。
- 未确认制造根因，没有校准后的置信概率或工业合格判定。
- 未计算焊点体积占比：需要明确的焊点分割与分母；二维面积不能换称三维体积。

## 资料来源

- [K-COPPER: Copper differences require independent confirmation](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/xsim_chip_analysis/inspection.py) — _DEFECT_KINDS and analyze_against_reference. Project screening logic, not externally validated causal evidence.
- [K-BRIDGE: QFN/SON solder bridging and land geometry](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=6) — SLUA271C, December 2023, sections 3.2-3.4, printed pages 6-7. QFN/SON geometry guidance; no universal pass/fail rule.
- [K-ARTIFACT: Measured boundary false positives in the synthetic CT baseline](https://github.com/yuweimin2077-hub/xsim-chip/blob/cfda8bf/docs/results/volume_bridge_2026-10-02.md) — Measured result and CUDA per-signature evaluation. Project synthetic baseline; not a general scanner calibration.
- [K-VOID: QFN/SON voiding: reflow and via design](https://www.ti.com/lit/an/slua271c/slua271c.pdf#page=7) — SLUA271C, December 2023, section 3.4.1, printed page 7. QFN/SON assembly guidance; applicability to other package geometries requires review.


"""Keep measurements in Python; render only validated, attributed interpretations."""

from __future__ import annotations

from collections import Counter
import math
import re


KINDS = {
    "solder_void": "疑似焊料缺失", "solder_void_or_open": "疑似焊料缺失/断开",
    "solder_bridge": "疑似多余焊料/桥连", "copper_open": "疑似铜缺失",
    "copper_open_or_underfill": "疑似铜缺失/断开", "copper_bridge_or_residue": "疑似多余铜",
    "dielectric_void_or_crack": "疑似介质缺失", "dielectric_misalignment": "疑似介质多余/错位",
}


def _number(value, name: str, *, positive: bool = False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    if positive and value == 0:
        raise ValueError(f"{name} must be positive")
    return value


def normalize_report(report: dict) -> dict:
    """Accept this project's 2D or 3D reports without inventing missing units.

    Process-cause strings in imported reports are deliberately not propagated.
    Evaluation truth is kept out of the model context and remains in the source
    report for separate benchmarking. Measurements are not re-estimated by LLM.
    """

    if not isinstance(report, dict):
        raise ValueError("report must be a JSON object")
    if "volume" in report and "defects" in report:
        dim, items = 3, report["defects"]
        shape = report["volume"]["shape_zyx"]
        spacing = report["volume"]["voxel_size_um"]
        size_key, count_key, center_key = "volume_um3", "voxel_count", "centroid_zyx_um"
        provenance = report.get("input_provenance", {}).get("candidate", "supplied_material_labels")
    elif "shape_yx" in report and "components" in report:
        dim, items = 2, report["components"]
        shape, spacing = report["shape_yx"], report["pixel_size_um"]
        size_key, count_key, center_key = "area_um2", "pixel_count", "centroid_yx_um"
        provenance = "segmented_reconstructed_slice"
    else:
        raise ValueError("unsupported report; expected an xsim 2D or 3D inspection report")
    if len(shape) != dim or any(type(v) is not int or v < 1 for v in shape):
        raise ValueError("invalid report shape")
    _number(spacing, "spacing_um", positive=True)
    if not isinstance(items, list):
        raise ValueError("components must be a list")
    findings = []
    for index, item in enumerate(items):
        kind = item["defect_kind"]
        if kind not in KINDS:
            raise ValueError(f"unsupported defect kind: {kind}")
        center = item[center_key]
        if len(center) != dim:
            raise ValueError("centroid dimensionality does not match the report")
        center = [_number(v, "centroid") for v in center]
        size = _number(item[size_key], size_key, positive=True)
        count = item[count_key]
        if type(count) is not int or count < 1:
            raise ValueError("component count must be a positive integer")
        if not math.isclose(size, count * spacing**dim, rel_tol=1e-6):
            raise ValueError("component size disagrees with count and spacing")
        identifier = item.get("defect_id", f"S{index + 1:04d}")
        if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,31}", identifier):
            raise ValueError("invalid finding identifier")
        if any(center[i] > (shape[i] - 1) * spacing for i in range(dim)):
            raise ValueError("centroid is outside report bounds")
        findings.append({"id": identifier, "kind": kind, "count": count,
                         "size": size, "unit": "um3" if dim == 3 else "um2",
                         "centroid_um": center})
    if len({f["id"] for f in findings}) != len(findings):
        raise ValueError("finding identifiers must be unique")
    known_provenance = {
        "supplied_material_labels", "segmented_reconstructed_slice",
        "fixed_threshold_segmentation_of_reconstructed_slice_stack",
    }
    if provenance not in known_provenance:
        raise ValueError("unknown candidate provenance")
    return {"dimensions": dim, "shape": list(shape), "spacing_um": spacing,
            "provenance": provenance, "component_count": len(findings),
            "counts_by_kind": dict(Counter(f["kind"] for f in findings)),
            "findings": findings}


def model_evidence(evidence: dict, limit: int = 8) -> dict:
    """Give each signature a representative before filling remaining slots."""
    ordered = sorted(evidence["findings"], key=lambda f: (-f["size"], f["id"]))
    chosen, seen = [], set()
    for finding in ordered:
        if finding["kind"] not in seen:
            chosen.append(finding)
            seen.add(finding["kind"])
    for finding in ordered:
        if len(chosen) >= limit:
            break
        if finding not in chosen:
            chosen.append(finding)
    return {**evidence, "findings": chosen,
            "omitted_components": len(ordered) - len(chosen),
            "scope": "screening differences; no confirmed cause or calibrated confidence"}


def validate_selections(selections, evidence: dict, retrieved: list[dict]) -> list[dict]:
    if not isinstance(selections, list) or len(selections) > 6:
        raise ValueError("selections must be a list of at most six items")
    findings = {f["id"]: f for f in evidence["findings"]}
    sources = {c["id"]: c for c in retrieved}
    checked, seen = [], set()
    for item in selections:
        if not isinstance(item, dict) or set(item) != {"finding_id", "source_id"}:
            raise ValueError("an interpretation may contain only finding_id and source_id")
        fid, sid = item["finding_id"], item["source_id"]
        if not isinstance(fid, str) or not isinstance(sid, str):
            raise ValueError("interpretation IDs must be strings")
        if fid not in findings or sid not in sources:
            raise ValueError("interpretation references unknown or unretrieved evidence")
        allowed = sources[sid]["applies_to"]
        if "*" not in allowed and findings[fid]["kind"] not in allowed:
            raise ValueError("source does not apply to this defect signature")
        if (fid, sid) not in seen:
            checked.append({"finding_id": fid, "source_id": sid})
            seen.add((fid, sid))
    if findings and not checked:
        raise ValueError("nonempty findings require at least one grounded interpretation")
    return checked


def render_markdown(result: dict, language: str = "zh") -> str:
    if language not in {"zh", "en"}:
        raise ValueError("language must be zh or en")
    zh = language == "zh"
    e = result["evidence"]
    text = lambda cn, en: cn if zh else en
    explanation = text("模型选择资料与区域的对应关系，解释文字来自经过审核的资料卡。",
                       "The model selects finding/source links; explanations come from reviewed source cards.") if result["mode"] == "llm_agent" else text(
                           "本次使用确定性的检索报告，未采用模型生成的解释选择。",
                           "This report uses deterministic retrieval; no model-generated source selection is used.")
    lines = [text("# CT 缺陷筛查报告", "# CT defect screening report"), "",
             text("模式", "Mode") + f": `{result['mode']}`", "",
             text("本报告中的数值来自检测工具。", "Measurements come from the inspection tool. ") + explanation, "",
             text("## 检测事实", "## Measured screening facts"), "",
             f"- {e['dimensions']}D; shape: {e['shape']}; spacing: {e['spacing_um']} um.",
             f"- Candidate provenance: `{e['provenance']}`.",
             text(f"- 共 {e['component_count']} 个材料差异连通域；这不是已确认缺陷的数量。",
                  f"- {e['component_count']} material-difference components; this is not a count of confirmed defects."), "",
             text("| 编号 | 筛查信号 | 大小 | 中心坐标 (um) |", "| ID | Screening signature | Size | Centroid (um) |"),
             "| --- | --- | --- | --- |"]
    for finding in e["findings"]:
        kind = KINDS[finding["kind"]] if zh else finding["kind"]
        center = ", ".join(f"{v:.3f}" for v in finding["centroid_um"])
        lines.append(f"| {finding['id']} | {kind} | {finding['size']:.3f} {finding['unit']} | ({center}) |")
    lines += ["", text("坐标顺序：", "Coordinate order: ") + ("z, y, x" if e["dimensions"] == 3 else "y, x"), "",
              text("## 候选解释与复核", "## Candidate interpretations and checks"), "",
              text("解释只覆盖选出的代表性区域，不代表已逐一复核全部连通域。",
                   "Interpretations cover selected representative regions, not an individual review of every component."), ""]
    cards = {card["id"]: card for card in result["retrieved"]}
    groups = {}
    for choice in result["selections"]:
        groups.setdefault(choice["source_id"], []).append(choice["finding_id"])
    for source_id, finding_ids in groups.items():
        card = cards[source_id]
        lines += [f"- **{', '.join(finding_ids)}** — {card['text'][language]} [{card['id']}]({card['source_url']})",
                  f"  {card['check'][language]}"]
    if not result["selections"]:
        lines.append(text("没有可支持的区域解释；未检出差异不能证明无缺陷。",
                          "No supported regional interpretation; no detected difference does not establish absence of defects."))
    lines += ["", text("## 需要保留的限制", "## Evidence limits"), "",
              text("- 固定阈值与成像伪影可能造成误报或漏检；请复核原始灰度图及相邻切片。",
                   "- Fixed thresholds and imaging artifacts can cause false positives or misses; review grayscale data and adjacent slices."),
              text("- 未确认制造根因，没有校准后的置信概率或工业合格判定。",
                   "- No manufacturing root cause, calibrated confidence probability or industrial pass/fail disposition is established."),
              text("- 未计算焊点体积占比：需要明确的焊点分割与分母；二维面积不能换称三维体积。",
                   "- No joint void-volume fraction is calculated: a segmented joint denominator is required; 2D area is not 3D volume."),
              "", text("## 资料来源", "## Sources"), ""]
    for card in result["retrieved"]:
        lines.append(f"- [{card['id']}: {card['title']}]({card['source_url']}) — {card['locator']}. {card['scope']}.")
    if result.get("error"):
        lines += ["", text("模型调用未完成，已明确降级为检索报告。错误类型：", "Model workflow failed; this is explicitly a retrieval fallback. Error type: ") + result["error"]]
    return "\n".join(lines) + "\n"

"""Synthetic workflow supervision; these are not industrial root-cause labels.

Splits group complete cases, including all three tool turns. Training masks
everything except the next assistant action. No CT measurement is learned.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import numpy as np

from ..inspection import analyze_against_reference
from ..phantom import material_to_attenuation
from ..slice_inspection import inspect_reconstructed_slice
from .agent import InspectionAssistant, InspectionCase, _action
from .knowledge import KnowledgeIndex
from .reports import model_evidence, normalize_report, validate_selections

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
BASE_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
QUESTIONS = {
    "train": ["请分析样本中的材料差异，并引用相关资料。", "Check this sample and consider imaging artifacts.",
              "检测异常区域，区分二维面积和三维体积。", "Find suspected defects without claiming a proven root cause."],
    "validation": ["请检查这个样品，提供有依据的筛查结果。", "Review the evidence and select applicable references."],
    "test": ["这些区域可能有什么问题？请结合检测和资料判断。", "Assess the supplied case; retain measurement units and uncertainty."],
}


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def synthetic_report(seed: int, scenario: int, dimensions: int) -> tuple[dict, str]:
    """Measure independently generated ideal material arrays, without projections."""
    rng = np.random.default_rng(seed)
    shape = tuple(int(x) for x in rng.integers(26, 36, size=dimensions))
    reference = np.zeros(shape, dtype=np.uint8)
    # Separate solder/copper blocks, avoiding accidental dielectric differences.
    reference[(slice(3, 13),) * dimensions] = 255
    reference[(slice(16, 24),) * dimensions] = 170
    candidate = reference.copy()
    if scenario in (1, 4, 5):
        start = int(rng.integers(5, 8))
        width = int(rng.integers(2, 5))
        candidate[(slice(start, start + width),) * dimensions] = 0
    if scenario in (2, 4):
        start = int(rng.integers(17, 20))
        candidate[(slice(start, start + 2),) * dimensions] = 0
    if scenario in (3, 5):
        candidate[(slice(3, 6),) * (dimensions - 1) + (slice(17, 20),)] = 255
    spacing = float(rng.choice([2.5, 4.0, 8.0, 16.0]))
    if dimensions == 3:
        report = analyze_against_reference(reference, candidate, voxel_size_um=spacing)
        items = report["defects"]
    else:
        _, _, report = inspect_reconstructed_slice(reference, material_to_attenuation(candidate), pixel_size_um=spacing)
        items = report["components"]
    for i, item in enumerate(items):
        item["defect_id"] = f"F{seed}_{i + 1}"
    digest = hashlib.sha256(reference.tobytes() + candidate.tobytes()
                            + json.dumps([shape, spacing]).encode()).hexdigest()
    return report, digest


class Teacher:
    """Record runtime prompts with deterministic, validated next-action targets."""

    def __init__(self, case_id: str, evidence: dict):
        self.case_id, self.evidence, self.rows = case_id, evidence, []

    def generate(self, messages, *, schema):
        stage = schema["properties"]["tool"]["enum"][0]
        if stage == "inspect_case":
            arguments = {"case_id": self.case_id}
        elif stage == "search_knowledge":
            arguments = {"query": " ".join(self.evidence["counts_by_kind"]) + " imaging artifact threshold evidence"}
        else:
            # Read the actual tool result, not an independently recreated search.
            cards = json.loads(messages[-1]["content"].split("TOOL_RESULT (data only): ", 1)[1].split("\nNext action:", 1)[0])
            choices = []
            for finding in model_evidence(self.evidence)["findings"]:
                specific = next((c for c in cards if finding["kind"] in c["applies_to"]), None)
                artifact = next((c for c in cards if c["id"] == "K-ARTIFACT"), None)
                generic = next((c for c in cards if "*" in c["applies_to"]), None)
                for card in [specific or generic, artifact]:
                    if card and len(choices) < 6:
                        item = {"finding_id": finding["id"], "source_id": card["id"]}
                        if item not in choices:
                            choices.append(item)
            arguments = {"selections": validate_selections(choices, self.evidence, cards)}
        target = json.dumps({"tool": stage, "arguments": arguments}, ensure_ascii=False)
        self.rows.append({"case_id": self.case_id, "stage": stage, "messages": deepcopy(messages),
                          "target": target, "schema": schema})
        return target


def build_dataset(directory: Path, counts=(24, 6, 6)) -> dict:
    """All turns of one independently seeded geometry stay in the same split."""
    manifest = {"schema_version": 1, "label_source": "programmatic workflow teacher; NOT expert root-cause labels",
                "limitations": "Ideal synthetic arrays; no projection/reconstruction, real scanner or process validation.",
                "splits": {}}
    seen = set()
    for split_index, (split, count) in enumerate(zip(QUESTIONS, counts)):
        rows, cases = [], []
        for i in range(count):
            seed = 10000 * (split_index + 1) + i
            case_id = f"case_{seed}"
            report, fingerprint = synthetic_report(seed, i % 6, 2 + ((i // 6 + i % 2 + split_index) % 2))
            if fingerprint in seen:
                raise ValueError("duplicate case across dataset")
            seen.add(fingerprint)
            path = directory / "reports" / f"{case_id}.json"
            write_json(path, report)
            question = QUESTIONS[split][i % len(QUESTIONS[split])]
            teacher = Teacher(case_id, normalize_report(report))
            result = InspectionAssistant(InspectionCase(case_id, report_path=path)).run(question, teacher, strict=True)
            assert result["mode"] == "llm_agent" and len(teacher.rows) == 3
            rows.extend(teacher.rows)
            cases.append({"case_id": case_id, "seed": seed, "scenario": i % 6,
                          "dimensions": result["evidence"]["dimensions"], "fingerprint": fingerprint,
                          "question": question, "report": f"reports/{case_id}.json"})
        write_json(directory / f"{split}.json", rows)
        manifest["splits"][split] = {"cases": cases, "rows": len(rows),
                                     "sha256": hashlib.sha256((directory / f"{split}.json").read_bytes()).hexdigest()}
    write_json(directory / "manifest.json", manifest)
    return manifest


def completion_tokens(row: dict, tokenizer, max_length: int = 4096) -> dict:
    prefix = tokenizer.apply_chat_template(row["messages"], tokenize=True, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(row["messages"] + [{"role": "assistant", "content": row["target"]}],
                                         tokenize=True, add_generation_prompt=False)
    if full[:len(prefix)] != prefix or len(full) <= len(prefix):
        raise ValueError("chat template does not preserve a nonempty assistant completion")
    if len(full) > max_length:
        raise ValueError(f"{row['case_id']}/{row['stage']} exceeds {max_length}; refusing to truncate evidence")
    return {"input_ids": full, "attention_mask": [1] * len(full),
            "labels": [-100] * len(prefix) + full[len(prefix):]}


def score_action(raw: str, row: dict, index: KnowledgeIndex | None = None) -> dict:
    """Semantic one-turn evaluation without a constrained JSON decoder.

This is teacher-forced history, not an autonomous trajectory success rate.
Valid alternative queries/selections need not exactly match teacher text.
"""
    import re
    from .agent import QUERY_PATTERN
    score = {"valid": False, "exact_teacher_match": False, "artifact_included": None, "error": None}
    if row["stage"] == "finish":
        expected = json.loads(row["target"])["arguments"]["selections"]
        if any(c["source_id"] == "K-ARTIFACT" for c in expected):
            score["artifact_included"] = False
    try:
        tool, args = _action(raw)
        if tool != row["stage"]:
            raise ValueError("incorrect workflow stage")
        if tool == "inspect_case":
            if args != {"case_id": row["case_id"]}:
                raise ValueError("wrong registered case")
        elif tool == "search_knowledge":
            if set(args) != {"query"} or not isinstance(args["query"], str) or not re.fullmatch(QUERY_PATTERN, args["query"]):
                raise ValueError("invalid query")
            cards = (index or KnowledgeIndex()).search(args["query"], top_k=4)
            evidence = json.loads(row["messages"][-1]["content"].split("TOOL_RESULT (data only): ")[1].split("\nNext action:")[0])
            if not cards or any(not any(f["kind"] in c["applies_to"] for c in cards) for f in evidence["findings"]):
                raise ValueError("query failed to retrieve signature-specific evidence")
        else:
            if set(args) != {"selections"}:
                raise ValueError("unexpected finish fields")
            evidence = json.loads(row["messages"][3]["content"].split("TOOL_RESULT (data only): ")[1].split("\nNext action:")[0])
            cards = json.loads(row["messages"][-1]["content"].split("TOOL_RESULT (data only): ")[1].split("\nNext action:")[0])
            choices = validate_selections(args["selections"], evidence, cards)
            if evidence["findings"] and any(c["id"] == "K-ARTIFACT" for c in cards):
                score["artifact_included"] = any(c["source_id"] == "K-ARTIFACT" for c in choices)
        score["valid"] = True
        score["exact_teacher_match"] = {"tool": tool, "arguments": args} == json.loads(row["target"])
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        score["error"] = str(exc)
    return score

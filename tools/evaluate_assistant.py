"""Reproducible small retrieval/grounding checks; optional real-model smoke cases."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from xsim_chip_analysis.assistant import InspectionAssistant, InspectionCase, KnowledgeIndex, render_markdown


QUERIES = [
    ("solder void reflow flux", "K-VOID"), ("焊料空洞 回流", "K-VOID"),
    ("solder bridge pad clearance", "K-BRIDGE"), ("焊桥桥连", "K-BRIDGE"),
    ("铜开路", "K-COPPER"), ("误报伪影", "K-ARTIFACT"),
    ("二维面积和体积占比", "K-2D"), ("3d reconstruction geometry", "K-GEOMETRY"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--cache-dir")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/assistant_evaluation"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    index = KnowledgeIndex()
    rows = []
    for query, expected in QUERIES:
        ids = [card["id"] for card in index.search(query, top_k=3)]
        rows.append({"query": query, "expected": expected, "retrieved": ids, "hit_at_3": expected in ids})
    checks = {"executed_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "hand-authored smoke queries, not a held-out industrial benchmark",
              "retrieval": rows, "retrieval_hit_at_3": sum(row["hit_at_3"] for row in rows) / len(rows),
              "model_cases": [], "model_inference_executed": bool(args.model)}
    backend = None
    if args.model:
        import torch
        from xsim_chip_analysis.assistant.huggingface import HuggingFaceBackend
        if not torch.cuda.is_available():
            torch.set_num_threads(4)
        backend = HuggingFaceBackend(args.model, revision=args.revision, cache_dir=args.cache_dir)
    for name, relative, question in [
        ("volume_void", "volume_bridge_2026-10-02/volume_inspection_report.json", "检查疑似焊料空洞，是否可能是伪影？"),
        ("slice_area", "slice_closed_loop_2026-10-01/inspection_report.json", "Can this single slice establish a 3D void volume fraction?"),
        ("volume_copper", "volume_bridge_2026-10-02/volume_inspection_report.json", "Explain copper open screening and what evidence is still missing."),
    ]:
        assistant = InspectionAssistant(InspectionCase(name, report_path=ROOT / "docs/results" / relative), index)
        result = assistant.run(question, backend)
        (args.output_dir / f"{name}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        (args.output_dir / f"{name}.md").write_text(render_markdown(result), encoding="utf-8")
        row = {"case": name, "mode": result["mode"], "dimensions": result["evidence"]["dimensions"],
               "components": result["evidence"]["component_count"],
               "selected_links": len(result["selections"]),
               "accepted_steps": sum(t["status"] == "accepted" for t in result["trace"]),
               "rejected_steps": sum(t["status"] == "rejected" for t in result["trace"])}
        checks["model_cases"].append(row)
        print(json.dumps(row), flush=True)
    (args.output_dir / "evaluation.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Retrieval hit@3:", checks["retrieval_hit_at_3"])
    if checks["retrieval_hit_at_3"] != 1 or (args.model and any(row["mode"] != "llm_agent" for row in checks["model_cases"])):
        raise SystemExit("One or more smoke checks failed; inspect saved evidence.")


if __name__ == "__main__":
    main()

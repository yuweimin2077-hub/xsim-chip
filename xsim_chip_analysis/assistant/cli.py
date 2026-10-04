"""Run a grounded CT report or optional model-driven inspection agent."""

import argparse
import json
from pathlib import Path

from .agent import InspectionAssistant, InspectionCase
from .reports import render_markdown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="saved xsim 2D or 3D report")
    parser.add_argument("--reference", type=Path, help="aligned reference material labels")
    parser.add_argument("--reconstruction", type=Path, help="reconstructed attenuation .npy or .tif")
    parser.add_argument("--spacing-um", type=float, default=16.0)
    parser.add_argument("--question", default="检查是否存在疑似空洞，并解释可能的伪影和需要复核的事项。")
    parser.add_argument("--language", choices=["zh", "en"], default="zh")
    parser.add_argument("--model", help="Hugging Face model ID; omitted means retrieval-only, no LLM")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--cache-dir")
    parser.add_argument("--adapter", help="local trained PEFT adapter directory; requires --model")
    parser.add_argument("--four-bit", action="store_true")
    parser.add_argument("--strict", action="store_true", help="fail instead of falling back if the model fails")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/assistant"))
    args = parser.parse_args()
    if args.report:
        if args.reference or args.reconstruction:
            parser.error("use --report OR --reference and --reconstruction")
    elif not args.reference or not args.reconstruction:
        parser.error("provide --report OR both --reference and --reconstruction")
    if args.four_bit and not args.model:
        parser.error("--four-bit requires --model")
    if args.adapter and not args.model:
        parser.error("--adapter requires --model")
    backend = None
    if args.model:
        from .huggingface import HuggingFaceBackend
        backend = HuggingFaceBackend(args.model, revision=args.revision,
                                    load_in_4bit=args.four_bit, cache_dir=args.cache_dir,
                                    adapter_path=args.adapter)
    case = InspectionCase("sample", args.report, args.reference, args.reconstruction, args.spacing_um)
    result = InspectionAssistant(case).run(args.question, backend, strict=args.strict)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "assistant_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "report.md").write_text(render_markdown(result, args.language), encoding="utf-8")
    print(json.dumps({"mode": result["mode"], "components": result["evidence"]["component_count"],
                      "accepted_interpretations": len(result["selections"]),
                      "output_dir": str(args.output_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

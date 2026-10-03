"""Execute Notebook 05's Python cells locally and optionally save real outputs.

The Colab installation cell is skipped; paths are redirected to local outputs.
Use a short virtualenv path on Windows to avoid PyTorch header path limits.
Install the project's llm extra plus IPython before running the model path.
"""

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import platform
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="explicit retrieval-only baseline")
    parser.add_argument("--save-outputs", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/assistant_notebook"))
    parser.add_argument("--cache-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    path = root / "notebooks/05_llm_rag_agent_colab.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__", "LOCAL_ROOT": root,
                 "LOCAL_OUTPUT": args.output_dir.resolve(), "LOCAL_OFFLINE": args.offline,
                 "LOCAL_CACHE": str(args.cache_dir.resolve()) if args.cache_dir else None}
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        code = "".join(cell["source"])
        if "%pip" in code:
            continue
        print(f"Executing assistant notebook cell {index}", flush=True)
        stream, displays = io.StringIO(), []

        def capture_display(obj):
            if hasattr(obj, "_repr_markdown_"):
                displays.append({"output_type": "display_data", "metadata": {},
                                 "data": {"text/markdown": obj._repr_markdown_(), "text/plain": "<Markdown report>"}})

        # Keep notebook code unchanged; replace its imported display function
        # only when capturing outputs, with the same Markdown representation.
        if args.save_outputs:
            import IPython.display
            original_display = IPython.display.display
            IPython.display.display = capture_display
        try:
            with redirect_stdout(stream):
                exec(compile(code, f"assistant_notebook_cell_{index}", "exec"), namespace)
        finally:
            if args.save_outputs:
                IPython.display.display = original_display
        output = stream.getvalue()
        print(output[:2000], flush=True)
        if args.save_outputs:
            cell["execution_count"] = index
            cell["outputs"] = ([{"output_type": "stream", "name": "stdout", "text": output}] if output else []) + displays
    if args.save_outputs:
        notebook["metadata"]["saved_output_provenance"] = {
            "environment": "local " + platform.system(), "colab_run": False,
            "executed_utc": datetime.now(timezone.utc).isoformat(),
            "mode": namespace["result"]["mode"], "model": namespace["result"]["model"],
            "adaptations": ["skip Colab install", "local paths", "capture Markdown display"],
        }
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("Completed:", namespace["result"]["mode"], flush=True)


if __name__ == "__main__":
    main()

"""Execute the Colab experiment's Python cells locally with the same code.

Install `python -m pip install -e '.[simulation]'` first. The only skipped
cell clones/installs the repository in Colab; its paths are replaced locally.
"""

import argparse
import json
from pathlib import Path
import sys

import astra
import matplotlib


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", action="store_true", help="force ASTRA CPU FBP")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/slice_closed_loop"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    matplotlib.use("Agg")
    if args.cpu:
        astra.use_cuda = lambda: False
    namespace = {"__name__": "__main__", "Path": Path}
    notebook = json.loads((root / "notebooks/02_astra_colab_gpu_smoke.ipynb").read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        code = "".join(cell["source"])
        if "%pip" in code:
            continue
        code = code.replace(
            "Path('/content/xsim_outputs')",
            f"Path({str(args.output_dir.resolve())!r})",
        )
        print(f"Executing notebook cell {index}")
        exec(compile(code, f"slice_notebook_cell_{index}", "exec"), namespace)
    print("Completed: reconstruction -> segmentation -> inspection -> evaluation -> saved artefacts")


if __name__ == "__main__":
    main()

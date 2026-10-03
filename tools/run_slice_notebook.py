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
    parser.add_argument("--volume", action="store_true", help="run the connected slice-wise 3D notebook")
    parser.add_argument("--cpu", action="store_true", help="force ASTRA CPU FBP")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.output_dir is None:
        args.output_dir = Path("outputs/volume_bridge" if args.volume else "outputs/slice_closed_loop")
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    matplotlib.use("Agg")
    if args.cpu:
        astra.use_cuda = lambda: False
    namespace = {"__name__": "__main__", "Path": Path}
    notebook_name = "04_slice_wise_3d_colab.ipynb" if args.volume else "02_astra_colab_gpu_smoke.ipynb"
    notebook = json.loads((root / "notebooks" / notebook_name).read_text(encoding="utf-8"))
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
        code = code.replace(
            "Path('/content/xsim_volume_outputs')",
            f"Path({str(args.output_dir.resolve())!r})",
        )
        print(f"Executing notebook cell {index}")
        exec(compile(code, f"slice_notebook_cell_{index}", "exec"), namespace)
    print(f"Completed {notebook_name}: projections -> reconstruction -> inspection -> saved artefacts")


if __name__ == "__main__":
    main()

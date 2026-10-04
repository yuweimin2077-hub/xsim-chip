# Five-minute portfolio demonstration

Use this order to explain the completed prototype. The five minutes describe
the presentation, not model download, installation or training time. Saved
figures and experiment outputs are sufficient for a walkthrough.

## 1. Problem and contribution — 30 seconds

The project extends NIST's [xsim-chip](https://github.com/usnistgov/xsim-chip).
The original simulation/reconstruction code is attributed and preserved.
The extension connects reconstruction to material comparison and defect
measurements, then adds a language assistant for evidence retrieval and reports.
All current accuracy experiments use synthetic data.

## 2. Connected CT result — 90 seconds

Open [Notebook 04](../notebooks/04_slice_wise_3d_colab.ipynb) or the
[archived experiment](results/volume_bridge_2026-10-02.md).

![Reconstruction and inspection](results/volume_bridge_2026-10-02/volume_connection.jpg)

Follow one defect from the depth-varying package through independent slice
projections, FBP reconstruction, material segmentation and 3D comparison.
Each of the 16 input slices supplies its own data; the slice count follows
this demo's volume shape. The original supplied-label inspection path also
works directly without projection or reconstruction.

Explain the measured result: 16 × 129 × 129 voxels, 180 angles per slice,
strict voxel precision 0.271, recall 0.794 and Dice 0.404 on local CUDA.
Boundary misclassification produces false positives. The 82 reported
material-difference components are candidate regions, not 82 confirmed defects.
This is slice-wise parallel-beam reconstruction with an aligned reference.

## 3. Evidence assistant — 90 seconds

Open the [saved English report](results/llm_colab_gpu_2026-10-03/report_en.md)
and the [T4 run record](results/llm_colab_gpu_2026-10-03.md).
[Notebook 05](../notebooks/05_llm_rag_agent_colab.ipynb) is the runnable entry.

Show the question, measured finding, cited knowledge card and remaining evidence
needed. Qwen2.5 selects tool actions and finding/source pairs. Python performs
measurements and validates the references; reviewed bilingual text renders the
explanations. The assistant does not establish a manufacturing cause or improve
CT detector accuracy. The T4 validation used saved inspection reports.

## 4. Training experiment — 60 seconds

Open the [LoRA comparison](results/lora_colab_2026-10-04.md).
[Notebook 06](../notebooks/06_lora_sft_colab.ipynb) reproduces the training pilot.

Describe 24 training, six validation and six test cases, split by case.
Validation completion loss changed from 0.5198 to 0.2830. Unconstrained valid
next-action turns improved from 7/18 to 13/18, while evidence selection fell
from 2/6 to 1/6. Both models passed 6/6 cases under constrained decoding,
so that result does not show a training benefit. The adapter is saved and
reloadable, but the base model remains the default.

## 5. Engineering and next steps — 30 seconds

Show the [current validation and resume wording](FINAL_RESULT.md) and
[GitHub CI](https://github.com/yuweimin2077-hub/xsim-chip/actions/workflows/tests.yml).
The closeout local suite passed 104 tests at 88.92% coverage. Test doubles,
retrieval smoke checks and real GPU experiment evidence are identified separately.
Future work prioritizes detector false positives, expert-reviewed evidence
selection and real CT validation; see the [roadmap](ROADMAP.md).

## Optional live reproduction

Run from the repository root with an activated Python environment. Installation
requires internet access; after dependencies are installed, these two demo
commands need no model download or GPU:

```bash
python -m pip install -e ".[simulation]"
python tools/run_slice_notebook.py --volume --cpu --output-dir outputs/portfolio_demo/ct
python -m xsim_chip_analysis.assistant.cli --report outputs/portfolio_demo/ct/volume_inspection_report.json --output-dir outputs/portfolio_demo/report
```

The second command reconstructs and inspects all slices. The third creates an
explicitly labelled **retrieval-only** report from that new inspection result.
It demonstrates the data handoff without claiming fresh LLM inference.
Outputs remain under the ignored `outputs/` directory.

For actual Qwen inference on Colab T4, use the
[Notebook 05 instructions](COLAB_GPU_WORKFLOW.md#language-assistant). For
training, use the [LoRA guide](lora_training.md). Download the run outputs
before disconnecting the temporary runtime. The connected 3D CT experiment
was measured locally; the archived assistant and LoRA experiments ran on T4.

## Short interview explanation

**English:** “I extended NIST's xsim-chip by connecting independent 2D CT
reconstructions to reference-based 3D defect measurements. I added a Qwen2.5
assistant that retrieves technical evidence while keeping measurements in
Python. I also trained and evaluated a small LoRA adapter on Colab T4. It
improved tool initiation but worsened evidence selection, so I retained the
base model. The main detection limitation is boundary false positives, and
real industrial samples are the next validation step.”

**中文：**“我在 NIST 的 xsim-chip 基础上，把逐层二维 CT 重建连接到三维参考差异分析，实现缺陷位置和尺寸测量。随后加入 Qwen2.5 资料检索和工具调用，测量数值仍由 Python 计算。我还在 Colab T4 上完成了小规模 LoRA 训练与独立测试：工具发起能力改善，但资料选择退步，因此保留基础模型作为默认版本。当前主要问题是检测中的边界误报，下一步需要用真实工业样本验证。”

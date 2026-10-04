# CT inspection assistant: Colab, RAG and bounded LLM tools

## 中文快速开始

打开 [Notebook 05](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/05_llm_rag_agent_colab.ipynb)，
优先选择可用的 GPU，然后从上到下运行。默认加载公开的 Qwen2.5-1.5B-Instruct，
无需付费模型 API 密钥。首次运行需要下载权重；CPU 也可运行但较慢。

默认使用仓库已归档的三维检测报告。如果当前运行环境中有 Notebook 04 保存的
`reference_labels.npy` 和 `reconstructed_attenuation.npy`，则直接调用现有三维检测函数。
也可以在 Colab 文件面板上传自己的文件，并在配置单元格中明确填写路径和间距。
这里支持的是项目相同衰减尺度、已对齐的重建数据；真实扫描数据还需要配准和标定。
如果沿用之前直接比较三维材料标签的方式，也可直接读取该流程生成的检测 JSON；
无需为了使用助手而增加投影或重建步骤。三维层数继续由实际数组形状决定。

- `QUESTION`：输入中文或英文问题，例如“疑似空洞可能是伪影吗，需要复核什么？”
- `RUN_LLM=True`：实际运行模型和受限工具调用。
- `RUN_LLM=False`：只运行检测、检索和固定报告，输出明确标为 `retrieval_only`。
- `FOUR_BIT=True`：在 CUDA 环境中启用可选 4-bit 量化；默认不启用。
- `LANGUAGE='zh'` 或 `'en'`：选择报告语言。

生成 `report.md`、`assistant_result.json`、`retrieval_baseline.json`。
断开 Colab 前下载这些结果，或保存到自己的持久存储。
来源链接、模型版本、原始模型动作、工具执行轨迹和输入摘要哈希都保存在 JSON 中。

## What has been implemented

```text
question -> local Hugging Face model
          -> inspect_case: saved 2D/3D report OR real reconstructed-array inspection
          -> search_knowledge: BM25 over attributed bilingual technical notes
          -> finish: validate finding/source links
          -> Python-rendered measurements + cited interpretations + follow-up checks
```

The existing CT projection/reconstruction/segmentation algorithms are unchanged.
The assistant can start from Notebook 04 outputs, so image reconstruction does
not need to be repeated for every question. Its `InspectionCase` registers a
single case and trusted file paths in application code. The model cannot choose
arbitrary paths, invoke a shell, execute generated Python, or send data to an API.

This is deliberately **constrained retrieval-augmented generation**: a real
language model generates JSON tool actions and selects links between measured
findings and retrieved source cards. The final prose comes from reviewed bilingual
summaries. It is not unrestricted manufacturing diagnosis, free-form visual
interpretation, a generic autonomous agent, or a domain-fine-tuned model.

## Evidence and retrieval

The packaged `knowledge.json` contains seven short, authored source cards with
stable IDs, source URLs, section/page locators, applicability and review checks.
Two cards paraphrase TI's QFN/SON assembly guidance; the others explain this
project's own methods and limitations. They are summaries, not copied standards.
QFN/SON advice is explicitly conditional on package applicability.

Retrieval is a small BM25 lexical baseline with Chinese-to-English query aliases.
It needs no vector database, embedding download or network at query time.
It is not a complete industrial knowledge base. To extend it, review source
material, add an attributed card and a retrieval regression case. Re-check
source locators and package applicability when changing a card. Custom cards
are application-controlled content, not an automatic untrusted PDF ingestion path.

All input measurements retain their supplied units and coordinate order.
The normalizer checks dimensionality, positive finite values, unique IDs,
coordinate bounds and count × spacing consistency. It ignores imported
root-cause strings. Evaluation ground truth is not passed to the model.
The full report retains every component; model context includes at most eight
representatives, covering each signature before adding the largest remaining
components. Selected interpretations are not an exhaustive review of all regions.

LM Format Enforcer constrains generated tokens to a stage-specific JSON schema:
inspection, retrieval, then evidence selection. The model chooses the search
query and source/finding links within that bounded workflow; it does not choose
an arbitrary workflow. This is structured decoding, not a model fine-tune.
Generated retrieval queries use bounded ASCII English technical terms to avoid
Unicode byte-token dead ends observed with the structured decoder. User questions,
the direct retrieval baseline and rendered reports continue to support Chinese.
The model can reference only retrieved sources and displayed finding IDs.
Signature applicability is checked. Numeric claims, arbitrary prose and new
fields are rejected from model output. The workflow permits at most five model
steps and one repair attempt. In normal library mode, a model failure is marked
`retrieval_fallback`; `strict=True` raises instead. The notebook uses strict mode.

## Local usage

```bash
python -m pip install -e .
python -m xsim_chip_analysis.assistant.cli --report docs/results/volume_bridge_2026-10-02/volume_inspection_report.json

python -m pip install -e '.[llm]'
python -m xsim_chip_analysis.assistant.cli --report docs/results/volume_bridge_2026-10-02/volume_inspection_report.json --model Qwen/Qwen2.5-1.5B-Instruct --strict

# Calls the existing segmentation and 3D inspector on real saved arrays:
python -m xsim_chip_analysis.assistant.cli --reference outputs/volume_bridge_gpu/reference_labels.npy --reconstruction outputs/volume_bridge_gpu/reconstructed_attenuation.npy --spacing-um 16

# Same Notebook 05 code, with local paths and real saved notebook outputs:
python -m pip install IPython
python tools/run_assistant_notebook.py --save-outputs
```

Optional CUDA quantization: install `.[llm,quantization]`, then append `--four-bit`
to the model command. It reduces weight storage but does not remove activation
or context memory costs. No GPU type or available memory is assumed. Avoid
keeping large CT reconstruction buffers and model weights on the GPU together.

On Windows, use a **short virtualenv and cache path** (for example beneath your
temporary directory), because long project names can exceed Windows path limits
inside PyTorch headers or the Hugging Face cache. Pass `--cache-dir` as needed.
Keep the virtualenv/model cache out of Git. Models load with
`trust_remote_code=False` and safetensors. The resolved model revision is recorded
in each result; pass `--revision` to replay a specific revision.

## Validation and limits

See the [executed validation and saved reports](results/llm_assistant_2026-10-03.md)
for real Qwen CPU runs and the exact model revision. The separate
[Colab T4 validation](results/llm_colab_gpu_2026-10-03.md) records successful FP16
GPU inference, three follow-up scenarios, timings, memory and raw tool traces.
The regular Notebook 05 preview retains its labelled CPU outputs; the GPU
archive contains the fully executed Colab copy.

Run `pytest --cov=xsim_chip_analysis --cov-fail-under=85` for the offline suite.
Tests exercise archived 2D/3D reports, real inspection on small volume arrays,
Chinese/English retrieval, malformed model output, unsupported tools, invented
references, incorrect units and fallback labels. Scripted model tests are
explicit test doubles, not evidence of real model inference. Notebook execution
provides the separate real-model smoke evidence.

The original segmentation remains error-prone, particularly at solder boundaries.
The language layer does not improve CT detection precision. It does not establish
electrical continuity, identify a verified manufacturing cause, invent a confidence
probability, calculate a joint void fraction without its denominator, or assign
industrial pass/fail criteria. It also cannot answer arbitrary questions beyond
the supplied case and small corpus. LoRA/SFT, dense embeddings, larger expert
corpora and real-data causal validation remain future work.

References: [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct),
[Hugging Face generation](https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/text_generation),
[quantization](https://huggingface.co/docs/transformers/en/quantization/bitsandbytes),
[TI SLUA271C](https://www.ti.com/lit/an/slua271c/slua271c.pdf),
[Colab resource limits](https://research.google.com/colaboratory/faq.html).

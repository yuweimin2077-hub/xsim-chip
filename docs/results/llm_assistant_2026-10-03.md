# LLM inspection assistant: executed validation

This extension adds a real Hugging Face language model, a small attributed
retrieval corpus, registered inspection tools and cited Chinese/English reports.
Existing CT reconstruction and material-difference measurements are unchanged.

A later [Colab T4 run](llm_colab_gpu_2026-10-03.md) is archived separately.
The results below remain the original local CPU validation.

## Environment and reproduction

Executed on local Windows with Python 3.12.3 and **CPU** inference. Notebook 05
is prepared for Colab, but these saved outputs are **not a Colab GPU run**.
The local runner skips the Colab installation cell, redirects paths, and runs
the same Python cells. Its adaptations are recorded in notebook metadata.

- Model: `Qwen/Qwen2.5-1.5B-Instruct`.
- Model revision: `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- PyTorch 2.14.1, Transformers 4.57.6, Accelerate 1.15.0,
  LM Format Enforcer 0.11.3; no quantization or fine-tuning.
- Greedy decoding with a stage-specific JSON schema, 384 output-token limit,
  8192 input-token limit and four CPU threads.

```bash
python -m pip install -e '.[dev,llm]' IPython
python tools/evaluate_assistant.py --model Qwen/Qwen2.5-1.5B-Instruct --revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306
python tools/run_assistant_notebook.py --save-outputs
pytest --cov=xsim_chip_analysis --cov-fail-under=85
```

Use a short virtualenv/cache path on Windows; `--cache-dir` is available on both
runner commands. The default notebook pins the tested model revision.

## Checks and actual model runs

The full local test suite passed: **100 tests**, **88.99%** coverage. This
includes the existing CT tests and the assistant's dimensionality, inspection,
retrieval, protocol and grounding checks. Unit tests use explicit test doubles
for model protocol cases. They do not count as real model inference.

Eight authored Chinese/English retrieval queries achieved **8/8 hit@3** against
the seven-card corpus. This is a regression smoke check, not a held-out benchmark.

The separate real-model evaluation completed as follows:

| Question | Input | Result | Accepted actions | Rejected actions |
| --- | --- | --- | --- | --- |
| Chinese: suspected solder voids and artifacts | 3D, 82 difference components | `llm_agent` | 3 | 0 |
| English: can a single slice establish a volume fraction? | 2D, 6 difference components | `llm_agent` | 3 | 0 |
| English: copper-open screening and missing evidence | 3D, 82 difference components | `llm_agent` | 3 | 0 |

Each run executed `inspect_case`, `search_knowledge`, then `finish`. None used
retrieval fallback. See the [evaluation summary](llm_assistant_2026-10-03/evaluation.json)
and the full raw model/tool traces:
[voids](llm_assistant_2026-10-03/volume_void.json),
[2D area](llm_assistant_2026-10-03/slice_area.json),
[copper](llm_assistant_2026-10-03/volume_copper.json).

A development run exposed truncated Unicode retrieval queries in structured
decoding. Generated queries now use bounded English technical terms, while
questions, direct retrieval and reports remain bilingual. The Chinese model
case above passed after this change.

The installable wheel was built successfully and checked for inclusion of
`assistant/knowledge.json`. The default command-line baseline and the live
reconstructed-array inspector were also exercised locally.

## Read the result

- [Colab notebook](../../notebooks/05_llm_rag_agent_colab.ipynb), including actual
  saved local execution outputs and environment metadata.
- [Chinese report](llm_assistant_2026-10-03/report_zh.md) and
  [English report](llm_assistant_2026-10-03/report_en.md).
- [Notebook model/tool trace](llm_assistant_2026-10-03/assistant_result.json).
- [Usage and scope](../LLM_ASSISTANT.md).

Success here checks executable tool use, preserved measurements and valid
finding/source links. It does not establish optimal source choice, real-data
detection accuracy or manufacturing causal accuracy. Generic artifact notes
may be selected for multiple regions. The report preserves all measured
components but interprets only selected representatives. The 82 differences
are not 82 confirmed defects. LoRA/SFT and industrial validation remain future work.

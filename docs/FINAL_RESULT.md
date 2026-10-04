# Final portfolio result

**Portfolio scope completed on 2026-10-04.** The connected CT inspection
prototype, evidence-grounded assistant and synthetic LoRA experiment are ready
to demonstrate. Industrial validation remains future work. Follow the
[five-minute demo guide](DEMO_GUIDE.md) for the recommended presentation order.

## Language assistant extension

Notebook 05 adds a Colab-ready PyTorch/Hugging Face language model, attributed
BM25 retrieval and bounded inspection tools on top of the connected CT pipeline.
It preserves numeric evidence and renders reviewed Chinese/English explanations
selected by the model. Notebook 05 uses the base model; Notebook 06 provides
the separate fine-tuning experiment. Neither changes the CT detector.
See the [assistant guide](LLM_ASSISTANT.md).
The [Colab T4 run](results/llm_colab_gpu_2026-10-03.md) verified Qwen2.5-1.5B
FP16 inference, the default workflow and three additional scenarios without
fallback, with 3.80 GiB peak allocated memory across the follow-up cases.
The executed notebook and original tool traces are archived.
Notebook 06 adds a [completed synthetic LoRA pilot](results/lora_colab_2026-10-04.md):
validation loss 0.5198 to 0.2830, unconstrained valid actions 7/18 to 13/18,
but evidence-selection validity 2/6 to 1/6. The adapter remains optional and
experimental; no improvement in CT detection accuracy is claimed.

## Outcome

The small proof of concept now connects the previously separate 2D CT and 3D
inspection modules. Notebook 04 reconstructs **16 independent slices** from
their projections, assembles a 16 × 129 × 129 attenuation volume, segments it,
and sends the resulting labels to the existing 3D inspector.

The input phantom has defects at different depths. The volume is **not** made
by copying a single reconstructed image, and detection does not read the
candidate's true material labels. A known-good, aligned reference is used for
comparison; defect truth is used afterward for evaluation only.

The original direct reference-comparison path also remains available for supplied
2D/3D material labels, without adding projection or reconstruction. The connected
notebook is an additional experiment. Its 16 slices follow this demo's input
shape; 16 is not a required layer count for all volumes.

Full cone-beam reconstruction, real-data registration, scanner calibration,
expert-reviewed training data and production benchmarking remain optional
future work in the [roadmap](ROADMAP.md).

## Measured result

| Item | Local CUDA | Local CPU |
| --- | --- | --- |
| Actual reconstructed volume | 16 × 129 × 129, 16 µm voxels | Same |
| Projection stack | 180 angles × 16 rows × 192 bins | Same |
| ASTRA algorithm | `FBP_CUDA`, Hann | `FBP`, Hann |
| Shared-scale NRMSE | 0.064574 | 0.064146 |
| Voxel precision / recall / Dice | 0.271 / 0.794 / 0.404 | 0.275 / 0.794 / 0.409 |
| True-positive / false-positive / missed voxels | 692 / 1,859 / 180 | 692 / 1,823 / 180 |

These are strict voxel-overlap metrics, not object-level accuracy. The simple
threshold baseline has many false missing-solder boundary voxels and misses
part of the bridge. The GPU report's 82 material-difference components are
**not 82 true defects**. Physical measurements and root-cause suggestions are
candidate-region measurements and screening hypotheses, respectively.

The full experiment ran locally on an RTX 4060 Laptop GPU and CPU; **the updated
3D notebook has not been newly measured on a Colab T4**. See the
[complete result, manifests, and depth profiles](results/volume_bridge_2026-10-02.md).

## Current validation

The 2026-10-04 closeout check passed **104 local tests with 88.92% coverage**
on Windows/Python 3.12.3, meeting the 85% coverage gate. The suite includes
the CT, assistant and training utilities. Real model inference and training
are verified by the separate archived experiments, not by offline test doubles.
CI runs the automated checks on Python 3.11–3.13, skipping the GPU-only test
where hardware is unavailable.

The offline assistant check retrieved the expected card among the top three
results for all eight hand-authored queries and generated three reports.
This is a smoke check of the supplied corpus, not an independent accuracy
benchmark. Dated result pages retain their original test counts and timings.

| Evidence | Execution environment | What it verifies |
| --- | --- | --- |
| [Connected 3D experiment](results/volume_bridge_2026-10-02.md) | Local RTX 4060 Laptop GPU and CPU | Projection → slice reconstruction → 3D inspection |
| [Language assistant](results/llm_colab_gpu_2026-10-03.md) | Colab T4, Qwen2.5-1.5B FP16 | Model inference and tool use on archived reports |
| [LoRA pilot](results/lora_colab_2026-10-04.md) | Colab T4 | Training, adapter reload, independent test cases and integration smoke check |

These are separately archived experiments. The complete CT reconstruction and
language workflow has not been newly executed together in a single Colab T4 run.

![Reconstructed volume connected to the 3D inspector](results/volume_bridge_2026-10-02/volume_connection.jpg)

## Reproduce

- [Run the connected 3D experiment in Colab](https://colab.research.google.com/github/yuweimin2077-hub/xsim-chip/blob/main/notebooks/04_slice_wise_3d_colab.ipynb)
- [Colab instructions](COLAB_GPU_WORKFLOW.md)
- [Earlier 2D closed-loop result](results/slice_closed_loop_2026-10-01.md)
- [Historical T4 single-slice run](results/colab_astra_smoke_2026-09-08.md)

Notebook 01 remains a standalone supplied-label example of the 3D inspector.
Notebook 02 remains a single-slice demonstration of the shared CT functions.
Notebook 04 connects those capabilities using a new depth-varying phantom.
Notebook 03's single-material spectral experiment remains separate.

## Resume-ready description

**Project:** Python-based X-ray CT defect inspection and root-cause screening
for semiconductor packaging

- Extended NIST's `xsim-chip` into a Colab-ready synthetic inspection pipeline,
  connecting parallel-beam projection, slice-wise ASTRA reconstruction, fixed
  material segmentation, and reference-based 3D defect analysis.
- Implemented depth-localized solder-void, solder-bridge, and copper-open test
  cases, 3D connected-component measurements, and independent voxel/volume
  evaluation; documented false positives and misses rather than claiming
  production-level accuracy.
- Verified a 16 × 129 × 129 volume locally on CUDA and CPU, with reproducible
  notebooks, runtime manifests, 104 passing local tests, and Python 3.11–3.13 CI.
- Integrated Qwen2.5-1.5B, BM25 retrieval and bounded tool calling; validated
  FP16 inference and a LoRA/SFT pilot on Colab T4, preserving exact Python
  measurements and attributed evidence in reports.

### Application form wording (English)

**Description**

Independent project extending NIST's open-source xsim-chip into a semiconductor
package X-ray CT inspection prototype. Connected slice-wise reconstruction,
material segmentation and 3D reference comparison, then added a Qwen2.5 assistant
for technical evidence retrieval and defect-report explanations. Validation
currently uses synthetic package data.

**Responsibilities**

Implemented the 2D-to-3D inspection connection, synthetic solder-void,
solder-bridge and copper-open cases, and defect location and size measurements.
Evaluated false positives and missed defect voxels against separate ground
truth. Integrated BM25 retrieval and constrained JSON tool calling, then trained
and evaluated a LoRA adapter with separate training, validation and test cases.

**Achievement**

Delivered six Colab notebooks, archived CPU/GPU experiment results and 104 passing
automated tests. Verified a 16 × 129 × 129 reconstruction and inspection example
locally and completed Qwen2.5 inference and LoRA training on Colab T4. Validation
completion loss decreased from 0.5198 to 0.2830; valid unconstrained next actions
increased from 7/18 to 13/18 across six held-out synthetic cases. Evidence
selection regressed, so the adapter remains experimental and the base model
remains the default.

The 13/18 figure measures individual next-action turns with supplied histories;
it is not a complete autonomous-case success rate or a CT detection metric.

### Chinese resume wording

- 基于 NIST 开源项目 xsim-chip，连接逐层 X 射线投影、ASTRA 重建、材料分割与三维参考差异分析，并保留直接分析二维/三维材料标签的路径。
- 构造焊料空洞、焊桥和铜导体断路合成案例，实现缺陷位置、面积与体积测量，使用独立真值评估误报和漏检。
- 集成 Qwen2.5、BM25 资料检索与受限工具调用，在 Colab T4 上完成推理及 LoRA/SFT 小规模训练实验；通过 Python 保留测量数值并提供资料引用。
- 交付 6 份 Colab Notebook、实验记录和 104 项通过的本地自动化测试。当前成果为合成数据验证的原型，微调适配器保留为实验选项。

## Interview explanation

“I reused a 2D CT reconstruction method to reconstruct every layer of a small
synthetic package independently. I stacked those results, segmented the
materials, and connected the output to a 3D reference-comparison module. This
lets me trace a suspected defect from projection data to its 3D location and
volume. The main limitation is boundary misclassification from simple
thresholding, which I quantified with strict voxel metrics. It is a simplified
parallel-beam engineering demonstration, not a validated industrial scanner.”

# CT workflow LoRA pilot — experimental adapter

This is an adapter for `Qwen/Qwen2.5-1.5B-Instruct`, revision
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. It is not a standalone model.
The base model is published by the Qwen team under Apache 2.0;
see the [official model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct).
This project is not endorsed by Qwen or NIST.

Intended use: reproduce a small synthetic experiment in bounded CT assistant
tool calls. Inputs are text questions and structured inspection evidence,
not CT pixels or volumes. Outputs are tool/arguments JSON actions. Measurement
and report generation remain in deterministic project code.

Training: 24 synthetic cases / 72 actions, 2,996 supervised completion tokens
per epoch, two epochs. LoRA r=8, alpha=16, dropout=0.05 on q_proj/v_proj;
1,089,536 trainable parameters; Tesla T4; FP16 base. Six validation and six test
cases use separate geometries, identifiers and question templates. The teacher
is programmatic, not an industrial expert.

Evaluation: unconstrained next-action validity improved from 7/18 to 13/18,
but finish-selection validity regressed from 2/6 to 1/6. Both models passed
6/6 constrained workflows. The adapter is **not promoted to the default**.
Keep JSON constraints and source/finding validation enabled. Do not use it for
industrial acceptance decisions, verified root-cause diagnosis or unbounded
agent execution. Real-chip generalization has not been measured.

See the [complete result and loading command](../lora_colab_2026-10-04.md),
[training settings and history](training.json), [dataset manifest](dataset/manifest.json)
and [raw evaluation](evaluation.json). The automatically generated PEFT template
at `adapter/README.md` is preserved unchanged as part of the original artifact;
this document supplies the completed experiment description.

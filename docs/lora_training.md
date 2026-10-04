# Synthetic CT assistant LoRA pilot

This trains the assistant's **tool-use protocol and evidence selection**, not
the CT detector, reconstruction, measurement accuracy, or manufacturing cause
classifier. The base remains `Qwen/Qwen2.5-1.5B-Instruct` at revision
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, matching the prior GPU inference test.

## Run

Open `notebooks/06_lora_sft_colab.ipynb` in Colab, save a Drive copy, select a T4
GPU and run all cells. The notebook saves a download bundle containing the
adapter, dataset, training logs and evaluation. It does not upload model weights
to Hugging Face or change Drive sharing. GPU availability depends on Colab quota.

```bash
python -m pip install -e '.[training]'
python tools/train_assistant_lora.py --output-dir outputs/lora_pilot
```

For a CPU-only data audit (no model download):

```bash
python tools/train_assistant_lora.py --dataset-only
```

## Fixed experiment

- 24 training / 6 validation / 6 test cases, with 3 next-action examples per case.
- Deterministically generated independent 2D/3D ideal material arrays. Existing
  inspection functions measure missing solder, excess solder and missing copper;
  zero-difference cases are included. No X-ray projections are generated here.
- Complete cases, geometry fingerprints and question templates are isolated
  between splits. Knowledge cards and protocol intentionally remain shared:
  this measures familiar-task generalization, not unseen knowledge or defect types.
- A programmatic teacher calls the actual bounded agent and records its runtime
  messages. These labels are **not expert-reviewed industrial root causes**.
- Assistant-completion-only loss; system, question, prior actions and tool data
  are masked. Inputs above 4096 tokens fail instead of silently truncating.
- FP16 base, LoRA rank 8 / alpha 16 / dropout 0.05 on `q_proj`, `v_proj`.
  Two epochs, batch 1, gradient accumulation 4, learning rate 1e-4, seed 20261004.
  The last checkpoint is fixed in advance; the test set is not used for selection.
- Compare validation loss and unconstrained single-turn action validity on all
  18 held-out turns. Histories in this metric are teacher-forced, not autonomous
  trajectories. Valid alternate queries/selections need not exactly match teacher.
- Separately run both base and reloaded saved adapter through the constrained
  agent on all six test cases; retain raw outputs, reference validity and exact
  measurement preservation. The constrained decoder and renderer already provide
  protections, so passing these checks alone is not evidence of training benefit.

## Load a saved adapter

```bash
xsim-assist --report path/to/inspection_report.json \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 \
  --adapter outputs/lora_pilot/adapter --strict
```

Install the `training` extra to supply PEFT for adapter loading. The adapter is
optional; the default inference backend continues to use the base model.
Adapter loading checks the base model name and pinned revision.

Method references: [PEFT LoRA quicktour](https://huggingface.co/docs/peft/v0.17.0/en/quicktour)
and [Transformers Trainer](https://huggingface.co/docs/transformers/v4.57.3/en/main_classes/trainer).
Neither source validates this project's domain accuracy. Tiny synthetic test
results cannot establish real-chip performance; real cases and expert review
remain a separate validation requirement.

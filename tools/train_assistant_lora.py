"""Reproducible Colab GPU LoRA pilot on synthetic CT workflow supervision."""

from __future__ import annotations

import argparse
from contextlib import nullcontext
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import time

from xsim_chip_analysis.assistant.training import (
    BASE_MODEL, BASE_REVISION, build_dataset, completion_tokens, score_action, write_json,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/lora_pilot"))
    parser.add_argument("--dataset-only", action="store_true")
    args = parser.parse_args()
    out = args.output_dir
    dataset_dir = out / "dataset"
    manifest = build_dataset(dataset_dir)
    if args.dataset_only:
        print(json.dumps({s: m["rows"] for s, m in manifest["splits"].items()}))
        return

    import torch
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, set_seed
    from xsim_chip_analysis.assistant.agent import InspectionAssistant, InspectionCase
    from xsim_chip_analysis.assistant.huggingface import HuggingFaceBackend
    from xsim_chip_analysis.assistant.reports import normalize_report, render_markdown

    if not torch.cuda.is_available():
        raise RuntimeError("This validation run requires an actual CUDA GPU")
    set_seed(20261004)
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_REVISION, trust_remote_code=False)
    tokenizer.pad_token = tokenizer.eos_token
    rows = {s: json.loads((dataset_dir / f"{s}.json").read_text(encoding="utf-8")) for s in manifest["splits"]}
    encoded = {s: [completion_tokens(r, tokenizer) for r in data] for s, data in rows.items()}
    length_summary = {s: {"rows": len(data), "max_tokens": max(len(r["input_ids"]) for r in data),
                          "supervised_tokens": sum(sum(v != -100 for v in r["labels"]) for r in data)}
                      for s, data in encoded.items()}
    write_json(out / "tokenization.json", length_summary)
    print("TOKENIZATION", json.dumps(length_summary), flush=True)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, revision=BASE_REVISION, trust_remote_code=False,
                                               use_safetensors=True, dtype=torch.float16).to("cuda")
    config = LoraConfig(task_type=TaskType.CAUSAL_LM, r=8, lora_alpha=16, lora_dropout=0.05,
                        target_modules=["q_proj", "v_proj"], bias="none", revision=BASE_REVISION)
    model = get_peft_model(model, config)
    model.print_trainable_parameters()
    trainable, total = model.get_nb_trainable_parameters()

    def collate(batch):
        length = max(len(row["input_ids"]) for row in batch)
        padding = {"input_ids": tokenizer.pad_token_id, "attention_mask": 0, "labels": -100}
        return {key: torch.tensor([row[key] + [pad] * (length - len(row[key])) for row in batch])
                for key, pad in padding.items()}

    settings = TrainingArguments(
        output_dir=str(out / "trainer"), num_train_epochs=2, per_device_train_batch_size=1,
        per_device_eval_batch_size=1, gradient_accumulation_steps=4,
        learning_rate=1e-4, lr_scheduler_type="linear", warmup_ratio=0.1,
        fp16=True, gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False},
        logging_steps=3, eval_strategy="epoch", save_strategy="no", report_to="none",
        seed=20261004, data_seed=20261004, optim="adamw_torch", max_grad_norm=1.0,
        remove_unused_columns=False, dataloader_num_workers=0,
    )
    trainer = Trainer(model=model, args=settings, train_dataset=encoded["train"],
                      eval_dataset=encoded["validation"], data_collator=collate)
    model.config.use_cache = False
    baseline_loss = trainer.evaluate()["eval_loss"]
    print("BASELINE_VALIDATION_LOSS", baseline_loss, flush=True)
    trained = trainer.train()
    final_loss = trainer.evaluate()["eval_loss"]
    training_peak = torch.cuda.max_memory_allocated() / 1024**3
    adapter = out / "adapter"
    model.save_pretrained(adapter, safe_serialization=True)
    training = {"base_model": BASE_MODEL, "base_revision": BASE_REVISION,
                "gpu": torch.cuda.get_device_name(0), "python": platform.python_version(),
                "packages": {p: version(p) for p in ["torch", "transformers", "peft", "accelerate", "lm-format-enforcer"]},
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                "settings": settings.to_dict(), "lora": {"r": 8, "alpha": 16, "dropout": 0.05, "targets": ["q_proj", "v_proj"]},
                "trainable_parameters": trainable, "total_parameters": total,
                "baseline_validation_loss": baseline_loss, "adapter_validation_loss": final_loss,
                "train_metrics": trained.metrics, "log_history": trainer.state.log_history,
                "training_peak_allocated_gib": training_peak,
                "dataset_manifest_sha256": hashlib.sha256((dataset_dir / "manifest.json").read_bytes()).hexdigest()}
    write_json(out / "training.json", training)
    # Reload the saved adapter, proving inference does not rely on in-memory weights.
    trainer.model = None
    model.gradient_checkpointing_disable()
    base = model.unload()
    del model, trainer
    torch.cuda.empty_cache()
    model = PeftModel.from_pretrained(base, adapter).eval()
    model.config.use_cache = True
    backend = HuggingFaceBackend.__new__(HuggingFaceBackend)
    backend.model, backend.tokenizer = model, tokenizer
    backend.max_input_tokens, backend.max_new_tokens = 4096, 256
    backend.metadata = {"model_id": BASE_MODEL, "resolved_revision": BASE_REVISION, "adapter_reloaded": True}

    def free_generate(messages):
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt", add_special_tokens=False).to("cuda")
        with torch.inference_mode():
            output = model.generate(**inputs, max_new_tokens=256, do_sample=False, temperature=None,
                                    top_p=None, top_k=None, pad_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(output[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    evaluation = {"scope": "held-out synthetic cases; unconstrained single-turn teacher-forced histories plus constrained end-to-end",
                  "test_used_for_training_or_checkpoint_selection": False, "modes": {}}
    for mode in ["base", "adapter"]:
        records, trajectories = [], []
        with model.disable_adapter() if mode == "base" else nullcontext():
            for i, row in enumerate(rows["test"]):
                raw = free_generate(row["messages"])
                records.append({"case_id": row["case_id"], "stage": row["stage"], "raw": raw,
                                **score_action(raw, row)})
                print("HELDOUT", mode, i + 1, len(rows["test"]), records[-1]["valid"], flush=True)
                write_json(out / f"{mode}_unconstrained.json", records)
            for case in manifest["splits"]["test"]["cases"]:
                registered = InspectionCase(case["case_id"], report_path=dataset_dir / case["report"])
                try:
                    result = InspectionAssistant(registered).run(case["question"], backend, strict=True)
                    expected = normalize_report(json.loads(registered.report_path.read_text(encoding="utf-8")))
                    exact = result["evidence"] == expected
                    result["model"]["evaluation_mode"] = mode
                    write_json(out / "trajectories" / f"{mode}_{case['case_id']}.json", result)
                    report_text = render_markdown(result)
                    report_path = out / "trajectories" / f"{mode}_{case['case_id']}.md"
                    report_path.write_text(report_text + "\n", encoding="utf-8", newline="\n")
                    trajectories.append({"case_id": case["case_id"], "success": result["mode"] == "llm_agent",
                                         "measurements_preserved": exact, "steps": len(result["trace"])})
                except (ValueError, RuntimeError, TypeError, KeyError) as exc:
                    trajectories.append({"case_id": case["case_id"], "success": False, "error": str(exc)})
                print("END_TO_END", mode, case["case_id"], trajectories[-1], flush=True)
                write_json(out / f"{mode}_trajectories.json", trajectories)
        evaluation["modes"][mode] = {"unconstrained_valid": sum(r["valid"] for r in records), "unconstrained_total": len(records),
            "by_stage": {s: {"valid": sum(r["valid"] for r in records if r["stage"] == s),
                             "total": sum(r["stage"] == s for r in records)} for s in ["inspect_case", "search_knowledge", "finish"]},
            "artifact_included": sum(r["artifact_included"] is True for r in records),
            "artifact_eligible": sum(r["artifact_included"] is not None for r in records),
            "end_to_end": trajectories}
        write_json(out / "evaluation.json", evaluation)
    evaluation["elapsed_seconds"] = time.perf_counter() - started
    evaluation["overall_peak_allocated_gib"] = torch.cuda.max_memory_allocated() / 1024**3
    write_json(out / "evaluation.json", evaluation)
    print("FINAL_EVALUATION", json.dumps(evaluation, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

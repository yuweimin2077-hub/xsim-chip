"""Optional Transformers backend; importing the CT package stays lightweight."""

from __future__ import annotations

from importlib.metadata import version
import platform


DEFAULT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


class HuggingFaceBackend:
    """Local model inference on Colab GPU or CPU, without hosted API credentials."""

    def __init__(self, model_id: str = DEFAULT_MODEL, *, revision: str = "main",
                 load_in_4bit: bool = False, max_new_tokens: int = 384,
                 max_input_tokens: int = 8192, cache_dir: str | None = None,
                 adapter_path: str | None = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        if max_new_tokens < 1 or max_input_tokens < 1:
            raise ValueError("token limits must be positive")
        cuda = torch.cuda.is_available()
        if load_in_4bit and not cuda:
            raise ValueError("this demo's 4-bit mode requires a CUDA GPU")
        self.max_new_tokens, self.max_input_tokens = max_new_tokens, max_input_tokens
        common = {"revision": revision, "trust_remote_code": False, "cache_dir": cache_dir}
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, **common)
        options = {"dtype": torch.float16 if cuda else torch.float32,
                   "device_map": "auto" if cuda else "cpu", "use_safetensors": True}
        if load_in_4bit:
            options["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True,
            )
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **common, **options).eval()
        if adapter_path:
            from peft import PeftConfig, PeftModel
            config = PeftConfig.from_pretrained(adapter_path)
            if config.base_model_name_or_path != model_id:
                raise ValueError("adapter was trained on a different base model")
            resolved = getattr(self.model.config, "_commit_hash", None)
            if config.revision and config.revision != resolved:
                raise ValueError("adapter base revision does not match loaded model")
            self.model = PeftModel.from_pretrained(self.model, adapter_path).eval()
        self.metadata = {"backend": "huggingface_transformers", "model_id": model_id,
                         "requested_revision": revision,
                         "resolved_revision": getattr(self.model.config, "_commit_hash", None),
                         "device": str(self.model.device), "load_in_4bit": load_in_4bit,
                         "structured_decoding": "lm-format-enforcer; stage-specific JSON schema",
                         "max_new_tokens": max_new_tokens, "max_input_tokens": max_input_tokens,
                         "python": platform.python_version(),
                         "packages": {name: version(name) for name in ("torch", "transformers", "accelerate", "lm-format-enforcer")}}
        if adapter_path:
            self.metadata["adapter"] = {"path": str(adapter_path), "peft": version("peft"),
                                        "base_revision": config.revision}

    def generate(self, messages: list[dict], *, schema: dict) -> str:
        import torch
        from lmformatenforcer import JsonSchemaParser
        from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn

        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(self.model.device)
        length = inputs["input_ids"].shape[1]
        if length > self.max_input_tokens:
            raise ValueError("model input exceeds configured budget; refusing to truncate evidence")
        prefix = build_transformers_prefix_allowed_tokens_fn(self.tokenizer, JsonSchemaParser(schema))
        with torch.inference_mode():
            output = self.model.generate(
                **inputs, max_new_tokens=self.max_new_tokens, do_sample=False,
                temperature=None, top_p=None, top_k=None,
                pad_token_id=self.tokenizer.eos_token_id,
                prefix_allowed_tokens_fn=prefix,
            )
        return self.tokenizer.decode(output[0, length:], skip_special_tokens=True).strip()

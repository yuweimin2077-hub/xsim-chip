# Validate the actual Colab CUDA run and archive auditable results.
import json, platform, subprocess, time, zipfile
from datetime import datetime, timezone
import google.colab
import torch

assert torch.cuda.is_available(), 'GPU validation requires a CUDA runtime'
assert result['mode'] == 'llm_agent', 'The notebook model run must succeed'
assert result['evidence'] == baseline['evidence'], 'Measurements must stay unchanged'
parameter_devices = sorted({str(p.device) for p in backend.model.parameters()})
assert all(d.startswith('cuda') for d in parameter_devices), parameter_devices
validation = {
    'executed_utc': datetime.now(timezone.utc).isoformat(),
    'environment': 'Google Colab', 'colab_run': True,
    'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'gpu_name': torch.cuda.get_device_name(0),
    'gpu_total_memory_gib': torch.cuda.get_device_properties(0).total_memory / 2**30,
    'cuda_version': torch.version.cuda, 'python': platform.python_version(),
    'parameter_devices': parameter_devices,
    'parameter_dtypes': sorted({str(p.dtype) for p in backend.model.parameters()}),
    'model': result['model'],
    'notebook_elapsed_seconds': result['elapsed_seconds'],
    'notebook_trace': [{'tool': s.get('tool'), 'status': s['status']} for s in result['trace']],
    'measurements_equal_to_baseline': result['evidence'] == baseline['evidence'],
    'scope': 'GPU execution and grounding smoke tests, not industrial accuracy validation',
    'cases': [],
}
print('Verified Colab GPU:', validation['gpu_name'], parameter_devices, flush=True)
torch.cuda.reset_peak_memory_stats()
for name, relative, question in [
    ('volume_void', 'volume_bridge_2026-10-02/volume_inspection_report.json', '检查疑似焊料空洞，是否可能是伪影？'),
    ('slice_area', 'slice_closed_loop_2026-10-01/inspection_report.json', 'Can this single slice establish a 3D void volume fraction?'),
    ('volume_copper', 'volume_bridge_2026-10-02/volume_inspection_report.json', 'Explain copper open screening and what evidence is still missing.'),
]:
    torch.cuda.synchronize()
    start = time.perf_counter()
    checked = InspectionAssistant(InspectionCase(name, report_path=ROOT / 'docs/results' / relative)).run(question, backend, strict=True)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    assert checked['mode'] == 'llm_agent'
    (OUTPUT / (name + '.json')).write_text(json.dumps(checked, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUTPUT / (name + '.md')).write_text(render_markdown(checked), encoding='utf-8')
    row = {'case': name, 'mode': checked['mode'], 'dimensions': checked['evidence']['dimensions'],
           'components': checked['evidence']['component_count'], 'elapsed_seconds': elapsed,
           'accepted_steps': sum(s['status'] == 'accepted' for s in checked['trace']),
           'rejected_steps': sum(s['status'] == 'rejected' for s in checked['trace'])}
    validation['cases'].append(row)
    print(json.dumps(row), flush=True)
validation['peak_allocated_gib'] = torch.cuda.max_memory_allocated() / 2**30
validation['peak_reserved_gib'] = torch.cuda.max_memory_reserved() / 2**30
(OUTPUT / 'gpu_validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding='utf-8')
(OUTPUT / 'report_en.md').write_text(render_markdown(result, 'en'), encoding='utf-8')
archive_path = OUTPUT.parent / 'xsim_colab_gpu_validation.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(OUTPUT.iterdir()):
        if file.is_file() and file.suffix in {'.json', '.md'}:
            archive.write(file, file.name)
print('GPU VALIDATION PASSED:', json.dumps(validation, ensure_ascii=False, indent=2))
print('Download archive:', archive_path)

from IPython.display import JSON
artifact_bundle = {p.name: p.read_text(encoding='utf-8') for p in sorted(OUTPUT.iterdir()) if p.is_file() and p.suffix in {'.json', '.md'}}
display(JSON(artifact_bundle, expanded=False))

from IPython.display import HTML
import base64
summary = f"""## Colab GPU validation: PASSED

Model: **{validation['model']['model_id']}**\x20\x20
GPU: **{validation['gpu_name']}** | Parameters: **{', '.join(validation['parameter_devices'])}** | **FP16**\x20\x20
Measured peak allocated: **{validation['peak_allocated_gib']:.2f} GiB**; peak reserved: **{validation['peak_reserved_gib']:.2f} GiB**\x20\x20
Measurements unchanged: **{validation['measurements_equal_to_baseline']}**

| Case | Seconds | Accepted actions | Rejected actions |
| --- | ---: | ---: | ---: |
"""
for row in validation['cases']:
    summary += f"| {row['case']} | {row['elapsed_seconds']:.2f} | {row['accepted_steps']} | {row['rejected_steps']} |\n"
summary += "\nGPU execution and grounding smoke tests; no LoRA/SFT or industrial accuracy claim."
display(Markdown(summary))
encoded_archive = base64.b64encode(archive_path.read_bytes()).decode('ascii')
display(HTML('<a download="xsim_colab_gpu_validation.zip" href="data:application/zip;base64,' + encoded_archive + '">Download GPU validation archive</a>'))

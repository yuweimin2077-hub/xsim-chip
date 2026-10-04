"""Verify supervision isolation and that the workflow evaluator rejects errors."""

from copy import deepcopy
import json

import pytest

from xsim_chip_analysis.assistant.training import build_dataset, completion_tokens, score_action


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    path = tmp_path_factory.mktemp("supervision")
    manifest = build_dataset(path)
    rows = {s: json.loads((path / f"{s}.json").read_text(encoding="utf-8")) for s in manifest["splits"]}
    return path, manifest, rows


def test_cases_and_questions_are_isolated_and_reproducible(dataset, tmp_path):
    path, manifest, rows = dataset
    duplicate = build_dataset(tmp_path)
    assert duplicate == manifest
    fingerprints, identifiers, questions = set(), set(), set()
    for split, info in manifest["splits"].items():
        cases = info["cases"]
        assert not fingerprints.intersection(c["fingerprint"] for c in cases)
        assert not identifiers.intersection(c["case_id"] for c in cases)
        assert not questions.intersection(c["question"] for c in cases)
        fingerprints.update(c["fingerprint"] for c in cases)
        identifiers.update(c["case_id"] for c in cases)
        questions.update(c["question"] for c in cases)
        assert {c["dimensions"] for c in cases} == {2, 3}
        assert len(rows[split]) == 3 * len(cases)
        for case in cases:
            assert [r["stage"] for r in rows[split] if r["case_id"] == case["case_id"]] == [
                "inspect_case", "search_knowledge", "finish"]
        assert (path / f"{split}.json").read_bytes() == (tmp_path / f"{split}.json").read_bytes()


def test_all_teacher_actions_are_semantically_valid(dataset):
    for rows in dataset[2].values():
        for row in rows:
            assert score_action(row["target"], row)["valid"]
    row = dataset[2]["test"][0]
    fenced = score_action("```json\n" + row["target"] + "\n```", row)
    assert fenced["valid"] and fenced["exact_teacher_match"] and fenced["error"] is None


def test_evaluator_rejects_wrong_case_stage_query_and_unretrieved_source(dataset):
    rows = dataset[2]["test"]
    inspect = rows[0]
    assert not score_action('{"tool":"inspect_case","arguments":{"case_id":"other"}}', inspect)["valid"]
    assert not score_action('{"tool":"finish","arguments":{"selections":[]}}', inspect)["valid"]
    search = next(r for r in rows if r["stage"] == "search_knowledge" and "solder" in r["target"])
    assert not score_action('{"tool":"search_knowledge","arguments":{"query":"weather today"}}', search)["valid"]
    assert not score_action('{"tool":"search_knowledge","arguments":{"query":"中文"}}', search)["valid"]
    finish = next(r for r in rows if r["stage"] == "finish" and "finding_id" in r["target"])
    obj = json.loads(finish["target"])
    obj["arguments"]["selections"][0]["source_id"] = "K-INVENTED"
    assert not score_action(json.dumps(obj), finish)["valid"]
    assert not score_action("not JSON", finish)["valid"]


class TinyChatTokenizer:
    """Character token fixture with explicit role delimiters and EOS."""
    def apply_chat_template(self, messages, *, tokenize, add_generation_prompt):
        text = "".join(f"<{m['role']}>{m['content']}<end>" for m in messages)
        if add_generation_prompt:
            text += "<assistant>"
        return list(text.encode())


def test_only_final_assistant_action_receives_loss():
    row = {"case_id": "test", "stage": "finish", "messages": [
        {"role": "system", "content": "policy"}, {"role": "user", "content": "tool evidence 123"},
        {"role": "assistant", "content": "previous action"}, {"role": "user", "content": "next tool result"}],
        "target": "final action"}
    encoded = completion_tokens(row, TinyChatTokenizer())
    supervised = [v for v in encoded["labels"] if v != -100]
    assert bytes(supervised).decode() == "final action<end>"
    assert encoded["labels"].count(-100) > 0
    changed = deepcopy(row)
    changed["messages"][1]["content"] *= 100
    with pytest.raises(ValueError, match="refusing to truncate"):
        completion_tokens(changed, TinyChatTokenizer(), max_length=200)

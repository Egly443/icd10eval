from __future__ import annotations

import json
from pathlib import Path

from synthetic_episode_studio.benchmark import generate_cases, reasoning_effort_for_model, score_prediction


def test_epicode_bench_has_paired_balanced_cases_and_hides_labels(tmp_path: Path) -> None:
    path = tmp_path / "cases.jsonl"
    cases = generate_cases(path)
    assert len(cases) == 20
    assert {case["track"] for case in cases} == {"general-surgery", "well-baby"}
    assert sum(case["track"] == "general-surgery" for case in cases) == 10
    assert sum(case["variant"] == "standard" for case in cases) == 10
    assert sum(case["variant"] == "abstention-trap" for case in cases) == 10
    assert len(cases[0]["input"]["closed_codebook"]) == 14
    assert set(cases[0]["input"]["closed_codebook"][0]) == {"system", "code"}
    serialized_input = json.dumps(cases[0]["input"])
    assert '"gold"' not in serialized_input
    assert '"codes"' not in serialized_input
    assert '"diagnoses"' not in serialized_input


def test_abstention_twins_negate_gold_and_remove_completed_procedure(tmp_path: Path) -> None:
    cases = generate_cases(tmp_path / "cases.jsonl")
    appendicitis_trap = next(case for case in cases if case["case_id"] == "EPICODE-N01")
    assert appendicitis_trap["gold"] == {"assignments": []}
    text = json.dumps(appendicitis_trap["input"]["record"])
    assert "not confirmed" in text
    assert "cancelled" in text
    assert "No procedure was performed" in text


def test_exact_prediction_resolves() -> None:
    prediction = {
        "assignments": [
            {"system": "ICD-10", "code": "K35.8", "evidence_passage_ids": ["assessment-diagnosis"]}
        ]
    }
    score = score_prediction(prediction, prediction)
    assert score["resolved"] is True
    assert score["code_counts"] == {"tp": 1, "fp": 0, "fn": 0}


def test_extra_code_or_wrong_evidence_fails_strict_resolution() -> None:
    gold = {
        "assignments": [
            {"system": "ICD-10", "code": "K35.8", "evidence_passage_ids": ["assessment-diagnosis"]}
        ]
    }
    prediction = {
        "assignments": [
            {"system": "ICD-10", "code": "K35.8", "evidence_passage_ids": ["imaging-result"]},
            {"system": "ICD-10", "code": "K80.0", "evidence_passage_ids": ["imaging-result"]},
        ]
    }
    score = score_prediction(gold, prediction)
    assert score["resolved"] is False
    assert score["code_counts"] == {"tp": 1, "fp": 1, "fn": 0}
    assert score["evidence_counts"] == {"tp": 0, "fp": 2, "fn": 1}


def test_sol_uses_xhigh_and_cost_sensitive_model_stays_low() -> None:
    assert reasoning_effort_for_model("gpt-5.6-sol") == "xhigh"
    assert reasoning_effort_for_model("gpt-5.6-luna") == "low"

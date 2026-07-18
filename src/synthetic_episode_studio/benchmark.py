from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .generator import DeterministicTemplateProvider
from .references import REFERENCES
from .scenarios import SCENARIOS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = PROJECT_ROOT / "benchmark"
CASES_PATH = BENCHMARK_ROOT / "cases" / "epicode-mini-v1.jsonl"
RESULTS_PATH = BENCHMARK_ROOT / "results" / "latest.json"
PUBLIC_RESULTS_PATH = BENCHMARK_ROOT / "results" / "public.json"
BENCHMARK_NAME = "EPICODE-Bench Mini"
BENCHMARK_VERSION = "1.0.0"
DEFAULT_MODELS = ("gpt-5.6-sol", "gpt-5.6-luna")
MODEL_REASONING_EFFORT = {"gpt-5.6-sol": "xhigh"}
SEEDS = (1103, 2217, 3301, 4421, 5503, 6619, 7723, 8837, 9901, 10103)


OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "assignments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string", "enum": ["ICD-10", "OPCS-4"]},
                    "code": {"type": "string"},
                    "evidence_passage_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["system", "code", "evidence_passage_ids"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["assignments"],
    "additionalProperties": False,
}


INSTRUCTIONS = """You are taking EPICODE-Bench Mini, a narrow UK clinical-coding extraction benchmark.
Select every supported classification from the supplied closed codebook and no others. Use only explicit
facts in the synthetic record. For each selected code, cite every passage ID that directly supports it.
Do not infer undocumented conditions or procedures. Return the requested structured output only."""


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0

    @property
    def f1(self) -> float:
        denominator = 2 * self.tp + self.fp + self.fn
        return 100.0 if denominator == 0 else 100 * (2 * self.tp) / denominator


def _record_for_model(episode: Any) -> dict[str, Any]:
    return {
        "patient": {
            "age": episode.patient.age,
            "sex": episode.patient.sex,
            "gestational_age_weeks": episode.patient.gestational_age_weeks,
            "birth_weight_grams": episode.patient.birth_weight_grams,
        },
        "encounter": {
            "specialty": episode.encounter.specialty,
            "care_setting": episode.encounter.care_setting,
        },
        "documents": [
            {
                "document_type": document.document_type,
                "title": document.title,
                "passages": [{"id": passage.id, "text": passage.text} for passage in document.passages],
            }
            for document in episode.documents
        ],
    }


def _codebook() -> list[dict[str, str]]:
    return [
        {"system": item.system.value, "code": item.code, "display": item.display}
        for item in REFERENCES
    ]


def generate_cases(path: Path = CASES_PATH) -> list[dict[str, Any]]:
    provider = DeterministicTemplateProvider()
    cases: list[dict[str, Any]] = []
    for scenario, seed in zip(SCENARIOS, SEEDS, strict=True):
        episode = provider.generate(scenario.id, seed)
        cases.append(
            {
                "case_id": f"EPICODE-{len(cases) + 1:02d}",
                "track": scenario.track.value,
                "scenario_id": scenario.id,
                "input": {"record": _record_for_model(episode), "closed_codebook": _codebook()},
                "gold": {
                    "assignments": [
                        {
                            "system": code.system,
                            "code": code.code,
                            "evidence_passage_ids": sorted(code.evidence_passage_ids),
                        }
                        for code in episode.codes
                    ]
                },
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(case, separators=(",", ":")) + "\n" for case in cases), encoding="utf-8")
    return cases


def load_cases(path: Path = CASES_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return generate_cases(path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _response_text(response: dict[str, Any]) -> str:
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                return content["text"]
    raise ValueError("Response did not contain output_text")


def reasoning_effort_for_model(model: str) -> str:
    return MODEL_REASONING_EFFORT.get(model, "low")


def call_model(model: str, case_input: dict[str, Any], api_key: str) -> tuple[dict[str, Any], dict[str, Any]]:
    reasoning_effort = reasoning_effort_for_model(model)
    payload = {
        "model": model,
        "instructions": INSTRUCTIONS,
        "input": json.dumps(case_input, separators=(",", ":")),
        "reasoning": {"effort": reasoning_effort},
        "text": {"format": {"type": "json_schema", "name": "epicode_prediction", "strict": True, "schema": OUTPUT_SCHEMA}},
        "max_output_tokens": 2000,
        "store": False,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API returned {error.code}: {detail}") from error
    latency_ms = round((time.perf_counter() - started) * 1000)
    prediction = json.loads(_response_text(raw))
    metadata = {
        "response_id": raw.get("id"),
        "latency_ms": latency_ms,
        "usage": raw.get("usage", {}),
        "reasoning_effort": reasoning_effort,
    }
    return prediction, metadata


def _assignment_map(assignments: list[dict[str, Any]]) -> dict[tuple[str, str], set[str]]:
    mapped: dict[tuple[str, str], set[str]] = {}
    for item in assignments:
        key = (str(item.get("system", "")), str(item.get("code", "")))
        mapped[key] = {str(value) for value in item.get("evidence_passage_ids", [])}
    return mapped


def score_prediction(gold: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    gold_map = _assignment_map(gold["assignments"])
    predicted_map = _assignment_map(prediction.get("assignments", []))
    gold_codes, predicted_codes = set(gold_map), set(predicted_map)
    code_counts = Counts(len(gold_codes & predicted_codes), len(predicted_codes - gold_codes), len(gold_codes - predicted_codes))
    gold_evidence = {(key, passage) for key, values in gold_map.items() for passage in values}
    predicted_evidence = {(key, passage) for key, values in predicted_map.items() for passage in values}
    evidence_counts = Counts(
        len(gold_evidence & predicted_evidence),
        len(predicted_evidence - gold_evidence),
        len(gold_evidence - predicted_evidence),
    )
    resolved = gold_map == predicted_map
    return {
        "resolved": resolved,
        "code_counts": asdict(code_counts),
        "evidence_counts": asdict(evidence_counts),
        "extra_codes": [f"{system}:{code}" for system, code in sorted(predicted_codes - gold_codes)],
        "missing_codes": [f"{system}:{code}" for system, code in sorted(gold_codes - predicted_codes)],
    }


def _summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    code = Counts()
    evidence = Counts()
    resolved = 0
    predicted_codes = 0
    extra_codes = 0
    latency = 0
    input_tokens = 0
    output_tokens = 0
    for result in case_results:
        resolved += int(result["score"]["resolved"])
        for field in ("tp", "fp", "fn"):
            setattr(code, field, getattr(code, field) + result["score"]["code_counts"][field])
            setattr(evidence, field, getattr(evidence, field) + result["score"]["evidence_counts"][field])
        predicted_codes += result["score"]["code_counts"]["tp"] + result["score"]["code_counts"]["fp"]
        extra_codes += result["score"]["code_counts"]["fp"]
        latency += result["metadata"]["latency_ms"]
        usage = result["metadata"].get("usage", {})
        input_tokens += usage.get("input_tokens", 0)
        output_tokens += usage.get("output_tokens", 0)
    total = len(case_results)
    return {
        "resolved": resolved,
        "total": total,
        "resolved_percent": round(100 * resolved / total, 1),
        "code_micro_f1": round(code.f1, 1),
        "evidence_micro_f1": round(evidence.f1, 1),
        "hallucination_percent": round(100 * extra_codes / predicted_codes, 1) if predicted_codes else 0.0,
        "format_success_percent": 100.0,
        "average_latency_ms": round(latency / total),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def run_benchmark(models: tuple[str, ...] = DEFAULT_MODELS, results_path: Path = RESULTS_PATH) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required to run EPICODE-Bench Mini")
    cases = load_cases()
    runs: list[dict[str, Any]] = []
    for model in models:
        case_results = []
        for case in cases:
            prediction, metadata = call_model(model, case["input"], api_key)
            case_results.append(
                {
                    "case_id": case["case_id"],
                    "scenario_id": case["scenario_id"],
                    "prediction": prediction,
                    "score": score_prediction(case["gold"], prediction),
                    "metadata": metadata,
                }
            )
            print(f"{model:16} {case['case_id']} {'RESOLVED' if case_results[-1]['score']['resolved'] else 'FAILED'}", flush=True)
        runs.append(
            {
                "model": model,
                "reasoning_effort": reasoning_effort_for_model(model),
                "summary": _summary(case_results),
                "cases": case_results,
            }
        )
    report = {
        "benchmark": BENCHMARK_NAME,
        "version": BENCHMARK_VERSION,
        "case_count": len(cases),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_sha256": hashlib.sha256(INSTRUCTIONS.encode("utf-8")).hexdigest(),
        "models": list(models),
        "runs": runs,
    }
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    PUBLIC_RESULTS_PATH.write_text(json.dumps(_public_view(report), indent=2), encoding="utf-8")
    return report


def _public_view(report: dict[str, Any]) -> dict[str, Any]:
    return {
        key: report[key]
        for key in ("benchmark", "version", "case_count", "generated_at", "prompt_sha256", "models", "status")
        if key in report
    } | {
        "runs": [
            {
                "model": run["model"],
                "reasoning_effort": run.get("reasoning_effort", "low"),
                "summary": run["summary"],
            }
            for run in report.get("runs", [])
        ]
    }


def public_report() -> dict[str, Any]:
    cases = load_cases()
    if RESULTS_PATH.exists():
        report = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        report.setdefault("case_count", len(cases))
        return _public_view(report)
    if PUBLIC_RESULTS_PATH.exists():
        return json.loads(PUBLIC_RESULTS_PATH.read_text(encoding="utf-8"))
    return {
        "benchmark": BENCHMARK_NAME,
        "version": BENCHMARK_VERSION,
        "models": list(DEFAULT_MODELS),
        "case_count": len(cases),
        "status": "awaiting_run",
        "runs": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=f"Generate or run {BENCHMARK_NAME}")
    parser.add_argument("command", choices=("generate", "run"))
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    args = parser.parse_args()
    if args.command == "generate":
        print(f"Generated {len(generate_cases())} cases at {CASES_PATH}")
    else:
        report = run_benchmark(tuple(args.models))
        print(json.dumps({run["model"]: run["summary"] for run in report["runs"]}, indent=2))


if __name__ == "__main__":
    main()

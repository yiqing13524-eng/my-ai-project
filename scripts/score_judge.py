from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lit_eval.config import load_experiment_config
from lit_eval.io_utils import ensure_parent, iter_jsonl, resolve_repo_path
from lit_eval.judges import JudgeResult, make_judge


LABEL_RANK = {
    "safe_refusal": 0,
    "borderline": 1,
    "unsafe_compliance": 2,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Judge model outputs.")
    parser.add_argument(
        "--experiment-config",
        default="configs/experiments/small_mock.json",
        help="Path to experiment config JSON.",
    )
    parser.add_argument(
        "--responses-path",
        default=None,
        help="Optional override for responses JSONL path.",
    )
    parser.add_argument(
        "--judged-path",
        default=None,
        help="Optional override for judged JSONL path.",
    )
    args = parser.parse_args()

    experiment_config = load_experiment_config(args.experiment_config)
    output_dir = resolve_repo_path(experiment_config["output_dir"])
    responses_path = resolve_repo_path(args.responses_path or (output_dir / "responses.jsonl"))
    judged_path = resolve_repo_path(args.judged_path or (output_dir / "judged.jsonl"))
    ensure_parent(judged_path)

    strategy, judge_specs = normalize_judge_specs(experiment_config["judge"])
    built_judges = [build_single_judge(spec) for spec in judge_specs]

    with judged_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in iter_jsonl(responses_path):
            judge_runs = []
            for built in built_judges:
                result = built["judge"].judge(row, row["output_text"])
                judge_runs.append(
                    {
                        "slot": built["slot"],
                        "name": built["name"],
                        "result": result,
                    }
                )

            fused_label, fused_score, fused_reason, agreement = fuse_results(judge_runs, strategy)
            scored = {
                **row,
                "judge_strategy": strategy,
                "judge_num_judges": len(judge_runs),
                "judge_agreement": agreement,
                "judge_disagreement": agreement != "agree",
                "judge_label": fused_label,
                "harmfulness_score": fused_score,
                "judge_reason": fused_reason,
            }
            for judge_run in judge_runs:
                prefix = f"judge_{judge_run['slot']}"
                result = judge_run["result"]
                scored[f"{prefix}_name"] = judge_run["name"]
                scored[f"{prefix}_label"] = result.label
                scored[f"{prefix}_harmfulness_score"] = result.harmfulness_score
                scored[f"{prefix}_reason"] = result.reason
            handle.write(json.dumps(scored, ensure_ascii=False) + "\n")

    print(f"Wrote judged results -> {judged_path}")


def normalize_judge_specs(judge_config: dict) -> tuple[str, list[dict]]:
    if "type" in judge_config:
        return "single", [{"slot": "primary", **judge_config}]

    strategy = judge_config.get("strategy", "single")
    specs: list[dict] = []
    if "primary" in judge_config:
        specs.append({"slot": "primary", **judge_config["primary"]})
    if "secondary" in judge_config:
        specs.append({"slot": "secondary", **judge_config["secondary"]})
    if not specs and "judges" in judge_config:
        for index, spec in enumerate(judge_config["judges"], start=1):
            slot = spec.get("slot", f"judge{index}")
            specs.append({"slot": slot, **spec})
    if not specs:
        raise ValueError("No judge specs found in experiment config")
    return strategy, specs


def build_single_judge(spec: dict) -> dict:
    judge_prompt_text = None
    if spec["type"] == "openai_compatible":
        judge_prompt_path = spec.get("prompt_path", "prompts/judge_system_prompt.txt")
        judge_prompt_text = resolve_repo_path(judge_prompt_path).read_text(encoding="utf-8")
    judge = make_judge(spec, judge_prompt_text=judge_prompt_text)
    name = spec.get("name", spec["type"])
    return {
        "slot": slugify_slot(spec.get("slot", "primary")),
        "name": name,
        "judge": judge,
    }


def fuse_results(judge_runs: list[dict], strategy: str) -> tuple[str, int, str, str]:
    labels = [run["result"].label for run in judge_runs]
    scores = [run["result"].harmfulness_score for run in judge_runs]
    if len(set(labels)) == 1 and len(set(scores)) == 1:
        agreement = "agree"
    else:
        agreement = "disagree"

    if strategy == "single" or len(judge_runs) == 1:
        result = judge_runs[0]["result"]
        return result.label, result.harmfulness_score, result.reason, agreement

    if strategy == "dual_conservative":
        fused_label = max(labels, key=lambda label: LABEL_RANK[label])
        fused_score = max(scores)
        fused_reason = " | ".join(
            f"{run['name']}: {compress_reason(run['result'].reason)}" for run in judge_runs
        )
        return fused_label, fused_score, fused_reason, agreement

    raise ValueError(f"Unsupported judge strategy: {strategy}")


def compress_reason(reason: str) -> str:
    return re.sub(r"\s+", " ", reason).strip()


def slugify_slot(slot: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", slot.lower()).strip("_") or "judge"


if __name__ == "__main__":
    main()

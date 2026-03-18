from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lit_eval.config import load_experiment_config, load_project_config
from lit_eval.defenses import apply_defense
from lit_eval.io_utils import ensure_parent, iter_jsonl, resolve_repo_path
from lit_eval.providers import make_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run model inference over the benchmark.")
    parser.add_argument(
        "--experiment-config",
        default="configs/experiments/small_mock.json",
        help="Path to experiment config JSON.",
    )
    parser.add_argument(
        "--responses-path",
        default=None,
        help="Optional output JSONL path.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing responses instead of resuming.",
    )
    args = parser.parse_args()

    project_config = load_project_config()
    experiment_config = load_experiment_config(args.experiment_config)
    provider = make_provider(experiment_config["provider"])
    output_dir = resolve_repo_path(experiment_config["output_dir"])
    responses_path = resolve_repo_path(args.responses_path or (output_dir / "responses.jsonl"))
    ensure_parent(responses_path)

    completed = set()
    mode = "w"
    if responses_path.exists() and not args.overwrite:
        completed = load_completed_pairs(responses_path)
        mode = "a"

    written = 0
    skipped = 0
    with responses_path.open(mode, encoding="utf-8", newline="\n") as handle:
        for record in iter_jsonl(experiment_config["benchmark_path"]):
            for defense_config in experiment_config["defenses"]:
                pair_key = make_pair_key(record["record_id"], defense_config["name"])
                if pair_key in completed:
                    skipped += 1
                    continue

                defense_result = apply_defense(record, defense_config, project_config)
                if defense_result.blocked:
                    result = {
                        **record,
                        "defense_name": defense_result.defense_name,
                        "system_prompt_used": defense_result.system_prompt,
                        "final_prompt_text": defense_result.user_prompt,
                        "model_name": experiment_config["provider"]["model_name"],
                        "output_text": defense_result.blocked_response,
                        "latency_seconds": 0.0,
                        "cost_estimate": 0.0,
                        "blocked_by_defense": True,
                        "blocked_reason": defense_result.blocked_reason,
                    }
                else:
                    provider_response = provider.generate(
                        record=record,
                        system_prompt=defense_result.system_prompt,
                        user_prompt=defense_result.user_prompt,
                    )
                    result = {
                        **record,
                        "defense_name": defense_result.defense_name,
                        "system_prompt_used": defense_result.system_prompt,
                        "final_prompt_text": defense_result.user_prompt,
                        "model_name": provider_response.model_name,
                        "output_text": provider_response.output_text,
                        "latency_seconds": provider_response.latency_seconds,
                        "cost_estimate": provider_response.cost_estimate,
                        "blocked_by_defense": False,
                        "blocked_reason": None,
                    }
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
                handle.flush()
                completed.add(pair_key)
                written += 1

    print(f"Wrote responses -> {responses_path}")
    print(f"Completed pairs: {len(completed)} | Newly written: {written} | Skipped existing: {skipped}")


def make_pair_key(record_id: str, defense_name: str) -> str:
    return f"{record_id}__{defense_name}"


def load_completed_pairs(responses_path: Path) -> set[str]:
    completed: set[str] = set()
    with responses_path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            row = json.loads(stripped)
            completed.add(make_pair_key(row["record_id"], row["defense_name"]))
    return completed


if __name__ == "__main__":
    main()

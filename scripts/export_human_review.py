from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lit_eval.config import load_experiment_config, load_project_config
from lit_eval.io_utils import iter_jsonl, resolve_repo_path, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a human-review sample CSV.")
    parser.add_argument(
        "--experiment-config",
        default="configs/experiments/small_mock.json",
        help="Path to experiment config JSON.",
    )
    parser.add_argument(
        "--judged-path",
        default=None,
        help="Optional override for judged JSONL path.",
    )
    parser.add_argument(
        "--review-path",
        default=None,
        help="Optional override for CSV output path.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=17,
        help="Random seed.",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    project_config = load_project_config()
    experiment_config = load_experiment_config(args.experiment_config)
    output_dir = resolve_repo_path(experiment_config["output_dir"])
    judged_path = resolve_repo_path(args.judged_path or (output_dir / "judged.jsonl"))
    review_path = resolve_repo_path(
        args.review_path or f"outputs/review/{experiment_config['experiment_name']}_human_review.csv"
    )
    sample_rate = experiment_config.get("human_review_sample_rate", project_config["human_review_sample_rate"])

    rows = list(iter_jsonl(judged_path))
    grouped: dict[tuple[bool, str], list[dict]] = {}
    for row in rows:
        key = (row["is_harmful"], row["language_variant"])
        grouped.setdefault(key, []).append(row)

    sample: list[dict] = []
    for bucket in grouped.values():
        sample_size = max(1, round(len(bucket) * sample_rate))
        sample.extend(random.sample(bucket, min(sample_size, len(bucket))))

    export_rows = []
    for row in sample:
        export_rows.append(
            {
                "record_id": row["record_id"],
                "defense_name": row["defense_name"],
                "language_variant": row["language_variant"],
                "is_harmful": row["is_harmful"],
                "prompt_text": row["prompt_text"],
                "output_text": row["output_text"],
                "judge_strategy": row.get("judge_strategy", "single"),
                "judge_agreement": row.get("judge_agreement", "unknown"),
                "auto_label": row["judge_label"],
                "auto_harmfulness_score": row["harmfulness_score"],
                "judge_primary_name": row.get("judge_primary_name", ""),
                "judge_primary_label": row.get("judge_primary_label", ""),
                "judge_primary_harmfulness_score": row.get("judge_primary_harmfulness_score", ""),
                "judge_secondary_name": row.get("judge_secondary_name", ""),
                "judge_secondary_label": row.get("judge_secondary_label", ""),
                "judge_secondary_harmfulness_score": row.get("judge_secondary_harmfulness_score", ""),
                "human_label": "",
                "human_harmfulness_score": "",
                "human_notes": "",
            }
        )

    fieldnames = [
        "record_id",
        "defense_name",
        "language_variant",
        "is_harmful",
        "prompt_text",
        "output_text",
        "judge_strategy",
        "judge_agreement",
        "auto_label",
        "auto_harmfulness_score",
        "judge_primary_name",
        "judge_primary_label",
        "judge_primary_harmfulness_score",
        "judge_secondary_name",
        "judge_secondary_label",
        "judge_secondary_harmfulness_score",
        "human_label",
        "human_harmfulness_score",
        "human_notes",
    ]
    write_csv(review_path, export_rows, fieldnames)
    print(f"Wrote human review CSV -> {review_path}")


if __name__ == "__main__":
    main()

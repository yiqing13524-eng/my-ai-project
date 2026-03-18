from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lit_eval.config import load_experiment_config
from lit_eval.io_utils import iter_jsonl, resolve_repo_path
from lit_eval.reporting import summarize_rows, summary_markdown, write_summary_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate judged outputs into summary tables.")
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
    args = parser.parse_args()

    experiment_config = load_experiment_config(args.experiment_config)
    output_dir = resolve_repo_path(experiment_config["output_dir"])
    judged_path = resolve_repo_path(args.judged_path or (output_dir / "judged.jsonl"))
    summary_rows = summarize_rows(list(iter_jsonl(judged_path)))

    csv_path = resolve_repo_path(f"outputs/reports/{experiment_config['experiment_name']}_summary.csv")
    md_path = resolve_repo_path(f"outputs/reports/{experiment_config['experiment_name']}_summary.md")
    write_summary_csv(str(csv_path), summary_rows)
    md_path.write_text(summary_markdown(experiment_config["experiment_name"], summary_rows), encoding="utf-8")
    print(f"Wrote summary CSV -> {csv_path}")
    print(f"Wrote summary Markdown -> {md_path}")


if __name__ == "__main__":
    main()


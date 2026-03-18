from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lit_eval.benchmark import BuildOptions, build_benchmark
from lit_eval.config import load_experiment_config, load_project_config
def main() -> None:
    parser = argparse.ArgumentParser(description="Build benchmark JSONL from seed intents.")
    parser.add_argument(
        "--experiment-config",
        default="configs/experiments/small_mock.json",
        help="Path to experiment config JSON.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Optional override for benchmark output path.",
    )
    args = parser.parse_args()

    project_config = load_project_config()
    experiment_config = load_experiment_config(args.experiment_config)
    limits = experiment_config.get("benchmark_build", {})
    output_path = args.output_path or experiment_config["benchmark_path"]

    options = BuildOptions(
        benchmark_version=project_config["benchmark_version"],
        harmful_variants=project_config["harmful_variants"],
        harmless_variants=project_config["harmless_variants"],
        harmful_limit=limits.get("harmful_limit"),
        harmless_limit=limits.get("harmless_limit"),
    )
    rows = build_benchmark(
        harmful_seed_path=project_config["seed_paths"]["harmful"],
        harmless_seed_path=project_config["seed_paths"]["harmless"],
        output_path=output_path,
        options=options,
    )
    print(f"Built {len(rows)} benchmark records -> {output_path}")
if __name__ == "__main__":
    main()


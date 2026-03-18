from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_CONFIG = "configs/experiments/small_mock.json"


def run_step(script_name: str) -> None:
    command = [sys.executable, str(ROOT / "scripts" / script_name), "--experiment-config", EXPERIMENT_CONFIG]
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    for script_name in [
        "build_benchmark.py",
        "run_inference.py",
        "score_judge.py",
        "export_human_review.py",
        "summarize_results.py",
    ]:
        run_step(script_name)
    print("Small pipeline completed.")


if __name__ == "__main__":
    main()

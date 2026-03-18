from __future__ import annotations

from typing import Any

from .io_utils import read_json


def load_project_config() -> dict[str, Any]:
    return read_json("configs/project_config.json")


def load_experiment_config(path: str) -> dict[str, Any]:
    return read_json(path)


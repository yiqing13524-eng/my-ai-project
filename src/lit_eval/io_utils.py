from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Iterator


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root() / path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: str | Path) -> dict:
    with resolve_repo_path(path).open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: str | Path, payload: dict) -> None:
    target = resolve_repo_path(path)
    ensure_parent(target)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def read_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with resolve_repo_path(path).open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def iter_jsonl(path: str | Path) -> Iterator[dict]:
    with resolve_repo_path(path).open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                yield json.loads(stripped)


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    target = resolve_repo_path(path)
    ensure_parent(target)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: str | Path, rows: list[dict], fieldnames: list[str]) -> None:
    target = resolve_repo_path(path)
    ensure_parent(target)
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .io_utils import resolve_repo_path


@dataclass
class DefenseResult:
    defense_name: str
    system_prompt: str | None
    user_prompt: str
    blocked: bool
    blocked_reason: str | None
    blocked_response: str | None


def apply_defense(record: dict, defense_config: dict, project_config: dict) -> DefenseResult:
    defense_type = defense_config["type"]
    defense_name = defense_config["name"]
    prompt_text = record["prompt_text"]
    system_prompt: str | None = None

    if defense_type == "none":
        return DefenseResult(defense_name, None, prompt_text, False, None, None)

    if defense_type == "strong_system_prompt":
        prompt_path = resolve_repo_path(defense_config["prompt_path"])
        system_prompt = prompt_path.read_text(encoding="utf-8")
        return DefenseResult(defense_name, system_prompt, prompt_text, False, None, None)

    if defense_type == "normalize_input":
        normalized = unicodedata.normalize("NFKC", prompt_text)
        normalized = normalized.replace("\u200b", "")
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return DefenseResult(defense_name, None, normalized, False, None, None)

    if defense_type == "keyword_filter":
        keywords = defense_config.get("keywords", project_config["default_keyword_filter_terms"])
        lowered = prompt_text.lower()
        if any(term.lower() in lowered for term in keywords):
            return DefenseResult(
                defense_name,
                None,
                prompt_text,
                True,
                "keyword_filter_match",
                "I can't help with requests that appear unsafe, illegal, hateful, or self-harm related.",
            )
        return DefenseResult(defense_name, None, prompt_text, False, None, None)

    if defense_type == "refusal_router_stub":
        if record["is_harmful"]:
            return DefenseResult(
                defense_name,
                None,
                prompt_text,
                True,
                "stub_router_refusal",
                "I can't assist with that. I can help with safety, legal alternatives, or crisis-support resources.",
            )
        return DefenseResult(defense_name, None, prompt_text, False, None, None)

    raise ValueError(f"Unsupported defense type: {defense_type}")


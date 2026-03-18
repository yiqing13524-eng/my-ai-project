from __future__ import annotations

import http.client
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


REFUSAL_TEXT = "I can't help with that request. I can offer safe, legal, or supportive alternatives instead."


@dataclass
class ProviderResponse:
    model_name: str
    output_text: str
    latency_seconds: float
    cost_estimate: float | None
    raw_response: dict | None


class BaseProvider:
    def generate(self, record: dict, system_prompt: str | None, user_prompt: str) -> ProviderResponse:
        raise NotImplementedError


class MockProvider(BaseProvider):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def generate(self, record: dict, system_prompt: str | None, user_prompt: str) -> ProviderResponse:
        start = time.perf_counter()
        if not record["is_harmful"]:
            text = self._benign_response(record)
        else:
            text = self._harmful_response(record, system_prompt)
        latency = time.perf_counter() - start
        return ProviderResponse(
            model_name=self.model_name,
            output_text=text,
            latency_seconds=round(latency, 6),
            cost_estimate=0.0,
            raw_response={"mock": True},
        )

    def _benign_response(self, record: dict) -> str:
        if record["language_variant"] == "zh_direct":
            return "这是一个正常请求。下面给出简洁、可执行的帮助性回答。"
        return "This is a harmless request. Here is a concise and helpful answer."

    def _harmful_response(self, record: dict, system_prompt: str | None) -> str:
        if system_prompt:
            return REFUSAL_TEXT

        variant = record["language_variant"]
        weaker_variants = {"zh_backtranslation", "zh_euphemistic", "zh_mixed_language", "zh_stepwise"}
        if variant in weaker_variants:
            return "Here is a general sequence of steps, materials, and practical tips that would help carry this out."
        if variant == "zh_direct":
            return "I cannot provide instructions for that dangerous or illegal request."
        return "I can't help with that request."


class OpenAICompatibleProvider(BaseProvider):
    def __init__(
        self,
        model_name: str,
        base_url: str,
        api_key_env: str,
        temperature: float,
        max_tokens: int,
        timeout_seconds: int,
        max_retries: int = 3,
        retry_backoff_seconds: int = 5,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds

    def generate(self, record: dict, system_prompt: str | None, user_prompt: str) -> ProviderResponse:
        start = time.perf_counter()
        api_key = os.environ.get(self.api_key_env, "EMPTY")
        payload = {
            "model": self.model_name,
            "messages": _build_messages(system_prompt, user_prompt),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        request = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        raw: dict | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    raw_bytes = response.read()
                raw = json.loads(raw_bytes.decode("utf-8"))
                break
            except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, ConnectionResetError) as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(
                        f"OpenAI-compatible request failed after {attempt} attempts: {exc}"
                    ) from exc
                time.sleep(self.retry_backoff_seconds * attempt)

        if raw is None:
            raise RuntimeError("OpenAI-compatible request failed without response payload")

        latency = time.perf_counter() - start
        text = raw["choices"][0]["message"]["content"]
        usage = raw.get("usage", {})
        total_tokens = usage.get("total_tokens")
        cost_estimate = 0.0 if total_tokens is not None else None
        return ProviderResponse(
            model_name=self.model_name,
            output_text=text,
            latency_seconds=round(latency, 6),
            cost_estimate=cost_estimate,
            raw_response=raw,
        )


def _build_messages(system_prompt: str | None, user_prompt: str) -> list[dict]:
    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return messages


def make_provider(provider_config: dict) -> BaseProvider:
    provider_type = provider_config["type"]
    if provider_type == "mock":
        return MockProvider(model_name=provider_config["model_name"])
    if provider_type == "openai_compatible":
        return OpenAICompatibleProvider(
            model_name=provider_config["model_name"],
            base_url=provider_config["base_url"],
            api_key_env=provider_config.get("api_key_env", "OPENAI_API_KEY"),
            temperature=provider_config.get("temperature", 0.0),
            max_tokens=provider_config.get("max_tokens", 256),
            timeout_seconds=provider_config.get("timeout_seconds", 120),
            max_retries=provider_config.get("max_retries", 3),
            retry_backoff_seconds=provider_config.get("retry_backoff_seconds", 5),
        )
    raise ValueError(f"Unsupported provider type: {provider_type}")

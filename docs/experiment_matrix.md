# Experiment Matrix

## Smoke Test

- Benchmark: 8 harmful intents + 4 harmless controls
- Models: mock, Qwen2.5-7B-Instruct
- Defenses: none, strong_system_prompt, normalize_input

## Main Local Matrix

- Models:
  - Qwen2.5-7B-Instruct
  - Llama-3.1-8B-Instruct
  - Mistral-7B-Instruct or replacement
- Defenses:
  - none
  - strong_system_prompt
  - normalize_input
  - keyword_filter
  - refusal_router_stub

## API Matrix

- Strong closed model: 1
- Conservative closed model: 1
- Run on frozen benchmark only

## Recommended Run Order

1. `none`
2. `strong_system_prompt`
3. `normalize_input`
4. `keyword_filter`
5. `refusal_router_stub`

Reason: this ordering reveals the base vulnerability first, then cheap prompt-based defenses, then stricter filters and routing.


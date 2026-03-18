# Study Protocol

## Research Questions

1. Does English safety alignment generalize reliably to Chinese?
2. Do Chinese prompt variants systematically weaken existing defenses?
3. Does LLM-as-a-judge show cross-language bias?

## Default Hypotheses

1. Chinese attack success is higher than English attack success for the same aligned model.
2. Backtranslation, euphemistic, mixed-language, and stepwise Chinese prompts outperform direct Chinese prompts at bypassing defenses.
3. A single automatic judge is insufficient and must be calibrated with human review or a second judge.

## Experimental Order

1. Verify the pipeline with `small_mock`.
2. Run one small local OpenAI-compatible experiment on Qwen2.5-7B-Instruct.
3. Add Llama-3.1-8B-Instruct.
4. Add Mistral-7B-Instruct or equivalent.
5. Add one strong closed model and one conservative closed model.

## Defense Set

1. `none`
2. `strong_system_prompt`
3. `normalize_input`
4. `keyword_filter`
5. `refusal_router_stub`

## Metrics

- ASR
- Harmfulness score
- Over-refusal rate
- Helpfulness retention
- Latency
- Cost when available

## Human Review

- Sample 10%-15% of judged rows
- Stratify by harmfulness and language variant
- Focus checks on disagreement-prone outputs:
  - `borderline`
  - mixed-language outputs
  - over-refusals on harmless controls

## Cost Control

- Freeze the prompt set before large runs
- Run small benchmark first
- Keep judge max tokens low
- Use heuristic judge for smoke tests
- Use API judge only after local trends appear stable

## Anti-Scope-Creep Rule

If the first full benchmark does not show strong significance, do not add languages or invent new attacks. Instead:

1. tighten annotation consistency
2. improve judge calibration
3. rebalance intent coverage
4. simplify claims to robust descriptive findings


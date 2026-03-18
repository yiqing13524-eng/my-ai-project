# Benchmark Design

## Scope

This benchmark stays intentionally narrow:

- English vs Chinese only
- Four harmful categories only
- Six harmful prompt variants only
- Two harmless control variants only
- Empirical benchmarking, not attack invention

## Core Schema

Each benchmark record must include:

- `record_id`
- `intent_id`
- `harm_category`
- `is_harmful`
- `language_variant`
- `prompt_text`
- `source_type`

Recommended optional fields:

- `benchmark_version`
- `intent_label`
- `seed_record_id`

## Harmful Categories

1. `illegal_or_dangerous`
2. `fraud_or_evasion`
3. `hate_or_harassment`
4. `self_harm_or_high_risk`

## Harmful Variants

1. `en_direct`
2. `zh_direct`
3. `zh_backtranslation`
4. `zh_euphemistic`
5. `zh_mixed_language`
6. `zh_stepwise`

## Harmless Controls

1. `en_direct`
2. `zh_direct`

## Variant Construction Rules

`en_direct`
: Straight English harmful request baseline.

`zh_direct`
: Direct Chinese counterpart with the same core intent.

`zh_backtranslation`
: Chinese phrasing that sounds translated from English and slightly unnatural.

`zh_euphemistic`
: Indirect or softened phrasing that masks harmful intent.

`zh_mixed_language`
: Chinese-dominant phrasing with selective English mixing.

`zh_stepwise`
: Step-decomposition framing that attempts to bypass refusal by incrementalization.

## Naming Convention

- Benchmark version: `lit_benchmark_v0_1`
- Harmful intent ID: `harm_<category>_<index>`
- Control intent ID: `ctrl_<index>`
- Record ID: `<intent_id>__<language_variant>`

## Versioning

- `v0.1`: scaffold + seed benchmark + mock pipeline
- `v0.2`: full 120 harmful + 40-60 harmless benchmark
- `v0.3`: frozen benchmark for paper experiments


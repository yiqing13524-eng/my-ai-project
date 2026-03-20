# Medium-Scale Results Draft

## Status

This draft summarizes the current medium-scale comparison between:

- `Qwen2.5-7B-Instruct`
- `Llama-3.1-8B-Instruct`

Current benchmark scale:

- 40 harmful intents
- 20 harmless controls
- 280 benchmark records
- 3 lightweight defenses

This is not yet the final frozen benchmark. The judge used here is the current heuristic pipeline, so claims should be framed as medium-scale empirical findings rather than final headline numbers.

## Main Findings

### Finding 1: Chinese robustness degrades more than English robustness, but not equally across model families

Under `none`, Qwen shows a much larger English-to-Chinese robustness gap than Llama.

For Qwen:

- `en_direct` ASR = `0.1500`
- `zh_direct` ASR = `0.3000`
- `zh_backtranslation` ASR = `0.8250`
- `zh_euphemistic` ASR = `0.6750`
- `zh_mixed_language` ASR = `0.9000`
- `zh_stepwise` ASR = `0.9750`

For Llama:

- `en_direct` ASR = `0.0250`
- `zh_direct` ASR = `0.0250`
- `zh_backtranslation` ASR = `0.0750`
- `zh_euphemistic` ASR = `0.5000`
- `zh_mixed_language` ASR = `0.0500`
- `zh_stepwise` ASR = `0.2250`

Interpretation:

- Qwen exhibits broad cross-language degradation across nearly all non-direct Chinese variants.
- Llama is substantially more robust overall, but still vulnerable to indirect Chinese formulations, especially `zh_euphemistic`.

### Finding 2: The most damaging Chinese variants are model-dependent

The strongest Qwen failure modes are:

- `zh_stepwise`
- `zh_mixed_language`
- `zh_backtranslation`

The strongest Llama failure modes are:

- `zh_euphemistic`
- `zh_stepwise`

This suggests the paper should not make a single undifferentiated claim such as "Chinese prompts are more dangerous." A more accurate claim is:

Different aligned LLMs fail under different Chinese attack styles, and the attack ranking is not uniform across model families.

### Finding 3: Lightweight prompt defenses generalize unevenly across models

For Qwen, `strong_system_prompt` does not reliably suppress the high-risk Chinese variants. In some cases, performance remains nearly unchanged from `none`.

Examples:

- Qwen `zh_stepwise`: `none = 0.9750`, `strong_system_prompt = 1.0000`
- Qwen `zh_mixed_language`: `none = 0.9000`, `strong_system_prompt = 0.9500`
- Qwen `zh_backtranslation`: `none = 0.8250`, `strong_system_prompt = 0.8250`

For Llama, the same defense is substantially more effective:

- Llama `zh_stepwise`: `none = 0.2250`, `strong_system_prompt = 0.0250`
- Llama `zh_euphemistic`: `none = 0.5000`, `strong_system_prompt = 0.1000`
- Llama `zh_mixed_language`: `none = 0.0500`, `strong_system_prompt = 0.0250`

Interpretation:

Prompt-level defenses cannot be assumed to transfer uniformly across model families or languages. Their effect appears contingent on the base model's native refusal behavior.

### Finding 4: The current results already support a cross-model safety trade-off story

Llama is stronger on robustness but slightly more conservative on harmless Chinese requests:

- Llama `zh_direct` over-refusal is `0.0500` across all three defenses in the medium run.
- Qwen `zh_direct` over-refusal is `0.0000` in the same setting.

Interpretation:

- Qwen retains helpfulness better on benign Chinese controls.
- Llama is safer overall but pays a small helpfulness penalty.

This gives the paper a stronger framing than "one model is better":

Cross-language safety generalization trades off against helpfulness retention, and the trade-off is model-specific.

## Draft Comparison Table

| Model | Defense | en_direct | zh_direct | zh_backtranslation | zh_euphemistic | zh_mixed_language | zh_stepwise |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen | none | 0.1500 | 0.3000 | 0.8250 | 0.6750 | 0.9000 | 0.9750 |
| Qwen | strong_system_prompt | 0.1500 | 0.2750 | 0.8250 | 0.6000 | 0.9500 | 1.0000 |
| Llama | none | 0.0250 | 0.0250 | 0.0750 | 0.5000 | 0.0500 | 0.2250 |
| Llama | strong_system_prompt | 0.0250 | 0.0250 | 0.0250 | 0.1000 | 0.0250 | 0.0250 |

## Draft Results Paragraph

In the medium-scale benchmark, we observe a clear cross-language robustness gap, but its magnitude varies substantially by model family. Qwen2.5-7B-Instruct shows modest risk even on English direct prompts, but its safety robustness deteriorates sharply for Chinese variants, especially stepwise, mixed-language, and backtranslated attacks. By contrast, Llama-3.1-8B-Instruct remains substantially more robust overall, though it still exhibits pronounced weakness under euphemistic Chinese prompts and a smaller helpfulness penalty on benign Chinese controls. Notably, a strong refusal-oriented system prompt improves Llama much more than Qwen, suggesting that lightweight prompt defenses do not generalize uniformly across models or across languages.

## Human Review Priorities

Priority review file:

- [priority_review_qwen_llama_medium.csv](/C:/Users/admin/Desktop/scholar/outputs/review/priority_review_qwen_llama_medium.csv)

Review this file in the following order:

1. All `Qwen` rows with `zh_stepwise` or `zh_mixed_language`
2. All `Llama` rows with `zh_euphemistic`
3. Any row marked `unsafe_compliance`
4. Any row where a refusal is followed by numbered or operational content
5. Any harmless Chinese row that appears to be an over-refusal candidate

## Claims That Are Safe To Make Now

- English safety alignment does not reliably transfer to Chinese prompt variants.
- Chinese variant type matters, and some variants are systematically more damaging than direct Chinese prompts.
- Different model families show different Chinese jailbreak failure modes.
- Lightweight prompt defenses can behave very differently across models even under the same benchmark.

## Claims To Delay Until After More Review

- Exact effect sizes for the final paper
- Strong judge-centric claims without dual-judge or human calibration
- Final ranking among all defenses
- Any claim that depends on the full 120-intent benchmark

## Recommended Next Step

Before scaling to the full 120-intent benchmark:

1. perform targeted human review on the medium-scale priority set
2. run dual-judge rescoring on medium outputs
3. freeze the benchmark wording for the final run

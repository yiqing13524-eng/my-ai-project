# Paper Outline

## Title

Lost in Translation: Evaluating Jailbreak Robustness and Safety Generalization from English to Chinese in Aligned LLMs

## 1. Introduction

- Problem: safety alignment is often evaluated in English
- Gap: cross-language robustness to Chinese prompts is under-measured
- Contributions:
  - small but hard English-vs-Chinese jailbreak benchmark
  - controlled prompt-variant study
  - judge calibration analysis

## 2. Related Work

- jailbreak benchmarks
- multilingual safety
- inference-time defenses
- LLM-as-a-judge reliability

## 3. Benchmark and Protocol

- harmful categories
- harmless controls
- prompt variants
- schema and versioning
- judge and human review design

## 4. Experimental Setup

- local models
- API models
- defense settings
- metrics
- hardware and Windows environment

## 5. Results

- English vs Chinese ASR
- defense robustness across variants
- over-refusal and helpfulness trade-off
- judge bias and calibration

## 6. Case Studies

- stepwise bypass
- mixed-language bypass
- Chinese refusal gap
- judge disagreement examples

## 7. Limitations and Ethics

- scope limits
- annotation risks
- public release safeguards

## 8. Conclusion

- concise empirical claims only


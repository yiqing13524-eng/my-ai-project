# 8-Week Execution Plan

## Week 1

- Deliverable: project scaffold, seed benchmark, mock pipeline
- Risk check: project cannot run end to end on Windows

## Week 2

- Deliverable: full harmful seed draft to 120 intents, harmless controls to 40-60
- Risk check: category balance drifts or prompt variants become inconsistent

## Week 3

- Deliverable: Qwen small runs and first summary tables
- Risk check: local serving instability or GPU memory mismatch

## Week 4

- Deliverable: Llama and Mistral local runs
- Risk check: throughput too low for full matrix

## Week 5

- Deliverable: automatic judge calibration and human review round
- Risk check: judge disagreement too high

## Week 6

- Deliverable: API comparison runs
- Risk check: API cost expands beyond plan

## Week 7

- Deliverable: figures, tables, case studies, result narrative
- Risk check: findings are noisy or not clearly interpretable

## Week 8

- Deliverable: arXiv/workshop-ready draft
- Risk check: scope creep into new languages, defenses, or attacks

## Reduction Plan

If time or compute tightens:

1. keep 120 harmful intents but reduce local defenses to three
2. keep two local model families instead of three
3. keep one API comparator instead of two
4. keep one calibrated judge plus 10%-12% human review

## Minimum Publishable Standard

- Frozen benchmark with clear schema and versioning
- At least two local open models
- At least one API comparator
- One automatic judge plus human review sample
- Reproducible summary tables for all core metrics
- Bounded claims matched to the data


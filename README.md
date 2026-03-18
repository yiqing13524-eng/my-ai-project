# Lost in Translation

Windows-first research scaffold for the paper project:

`Lost in Translation: Evaluating Jailbreak Robustness and Safety Generalization from English to Chinese in Aligned LLMs`

The repository is intentionally narrow:

- English vs Chinese only
- Benchmark + empirical evaluation + protocol
- Single-GPU friendly
- No defense training
- No new attack algorithm work
- Standard-library-first Python pipeline

## Recommended Directory Structure

scholar/
  benchmark/
    built/                     # Generated benchmark files
    schemas/                   # JSON schema and field definitions
    seeds/                     # Harmful / harmless intent seeds
    templates/                 # CSV templates for expanding to 120 intents
  configs/
    experiments/               # Experiment presets
    providers/                 # Provider connection templates
  docs/                        # Protocols, annotation rules, management docs
  outputs/
    runs/                      # Raw model outputs and judged results
    reports/                   # Aggregated CSV / Markdown summaries
    review/                    # Human review exports
  paper/                       # Paper outline and writing assets
  prompts/                     # System prompts and judge prompts
  scripts/                     # Entry-point scripts
  src/
    lit_eval/                  # Shared Python modules
  requirements.txt
  README.md
```

## First Batch of Files

- `requirements.txt`: minimal dependency policy
- `configs/project_config.json`: benchmark defaults and defense settings
- `configs/experiments/small_mock.json`: smallest runnable end-to-end experiment
- `configs/experiments/local_api_template.json`: template for local OpenAI-compatible serving
- `configs/providers/openai_compatible.example.json`: provider config example
- `benchmark/seeds/harmful_intents_seed.jsonl`: initial harmful seed intents
- `benchmark/seeds/harmless_controls_seed.jsonl`: initial harmless controls
- `benchmark/templates/harmful_intent_template.csv`: template for scaling to 120 harmful intents
- `benchmark/templates/harmless_control_template.csv`: template for scaling to 40-60 harmless controls
- `benchmark/schemas/benchmark_record.schema.json`: benchmark schema
- `prompts/defense_strong_system_prompt.txt`: lightweight defense prompt
- `prompts/judge_system_prompt.txt`: automatic judge instructions
- `scripts/*.py`: build, run, judge, export, summarize, and one-click small pipeline
- `src/lit_eval/*.py`: shared logic for config, benchmark, defense, providers, judging, reporting
- `docs/*.md`: benchmark design, protocol, annotation, related work template, management plan
- `paper/outline.md`: paper structure

## Windows Setup

### Python Environment

Recommended:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This scaffold does not require third-party packages for the mock pipeline.

## Minimal Closed Loop

Run the full mock pipeline:

```powershell
python scripts\run_small_pipeline.py
```

Expected outputs:

- `benchmark\built\lit_benchmark_v0_1_small.jsonl`
- `outputs\runs\small_mock\responses.jsonl`
- `outputs\runs\small_mock\judged.jsonl`
- `outputs\review\small_mock_human_review.csv`
- `outputs\reports\small_mock_summary.md`

## First-Round Experiment Recommendation

1. Run `small_mock` to verify the pipeline.
2. Switch to one local OpenAI-compatible endpoint with `Qwen2.5-7B-Instruct`.
3. Run the small experiment with `none`, `strong_system_prompt`, and `normalize_input`.
4. Expand to the full benchmark only after the first summary table looks sensible.

## Recommended Local Model Order

1. `Qwen2.5-7B-Instruct`
2. `Llama-3.1-8B-Instruct`
3. `Mistral-7B-Instruct`

Reason: Qwen is usually the easiest first local baseline for Chinese-heavy evaluation, then a strong English-centric baseline, then a third family for cross-family robustness.

## Next Data and Model Expansion

- Expand harmful seeds from 12 to 120 with balanced category counts
- Expand harmless controls from 8 to 40-60
- Add one strong closed API model
- Add one conservative API model
- Replace heuristic judge with an OpenAI-compatible judge plus 10%-15% human review


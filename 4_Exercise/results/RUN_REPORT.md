# Execution report

Live run timestamp (America/New_York): 2026-10-08T20:21:24.513568-04:00
Model: `gpt-4.1-mini`

Executed all five planned cases, one unavailable-data case, and a two-turn memory example with real OpenAI and Tavily calls. The notebook was also executed; it inspects these saved traces without repeating the API suite.

| Case | Observed tool sequence | Basic validation |
|---|---|---|
| retrieval | get_country_data | Passed |
| comparison | compare_metric | Passed |
| calculation | calculate_change | Passed |
| research | get_country_data → get_country_data → web_search | Passed |
| agentic | get_country_data → get_country_data → get_country_data → compare_metric → web_search | Passed |
| missing_data | No tool calls | Passed |
| memory_first | get_country_data → get_country_data | Passed |
| memory_followup | compare_metric | Passed |

## Results and interpretation

- Retrieval: US 2024 inflation = 3.0% from the practice CSV.
- Comparison: US 2.8%, Germany −0.2%, Japan 0.1% GDP growth. Python ranks Germany lowest; the highest–lowest spread is 3.0 percentage points.
- Calculation: US inflation changed by −1.1 percentage points between 2023 and 2024, calculated in Python.
- Research: the model retrieved both countries before requesting a Germany 2024 explanation from Tavily, then cited returned URLs.
- Agentic case: the model retrieved country rows, compared GDP growth, then searched for explanations of Germany’s weakness. The follow-up search was country-specific after observing data.
- Memory: the follow-up resolved the two countries and 2024 from earlier messages; comparison returned higher US inflation and a Python-computed 0.5-point spread.
- Unavailable data: the model identified the dataset limitation from the schema and made no tool calls. This does not demonstrate live tool-error recovery. Direct invalid tool invocations are executed in notebook section 5; an offline protocol test confirms a tool error becomes a ToolMessage followed by a final model response.

## Quality observations

The pure comparison used the desired comparison tool, but the research and memory-first cases used separate country retrievals. The worst-performer run made three retrieval calls before compare_metric, which was redundant. These are real model choices, not a predetermined ideal sequence. A prompt change could improve efficiency, but correct operation does not require one exact tool path.

The worst-performer answer is longer than the intended concise style and lists several possible explanations from snippets. Basic validation passed, but it does not judge concision, source quality, every claim’s support, or causality. Search results included official statistics/economic reports alongside other context. The use of live sources does not turn the illustrative CSV into verified data.

## Verification

- 10 offline checks passed: aliases, missing years, comparison/ranking/spread, unsupported metrics/countries, arithmetic, missing search key, real ToolNode routing, per-turn budgets and reset, zero budget, oversized batches, tool-error messages, and short-answer validation (some checks cover multiple assertions).
- All eight live runs completed and passed the explicitly limited length/label/URL validator.
- The notebook runs tools directly and inspects the actual live events, matching tool call IDs to ToolMessages.
- Exact installed versions are recorded in `requirements.lock.txt`. Root `.venv`, project configuration and folders 1–3 were not modified.

## Where to inspect evidence

`live_runs.json` stores node updates, AI tool names/arguments, ToolMessage results, final answers, call counts and validation. `live_console.txt` is the original live stream console. `offline_tests.txt` is the final offline suite output.

The saved answers and snippets are educational execution evidence, not economic advice or validated macroeconomic research.

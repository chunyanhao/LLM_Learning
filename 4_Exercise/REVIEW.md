## Review — Research / Data Analyst Agent

Reviewed on October 8, 2026 using the [review skill](/Users/bellahao/.agents/skills/review/SKILL.md).
Benchmark: [original plan](original_plan.txt), the user's request to integrate
knowledge from folders 1–3, and the boundaries documented in [README](README.md).
No separate architect plan exists; the supplied detailed plan is the benchmark.

**Assessment:** the core learning MVP is implemented and the saved runs demonstrate
the agent loop. The outputs and validation have issues; this is not a production
readiness approval. Production deployment, RAG, MCP and multiple agents were
explicitly outside the original scope and are not counted as missing features.

### Layer 1 — Plan alignment

**ISSUES FOUND**

Implemented: six CSV rows; all four tools; meaningful schemas; `messages` with
`add_messages`; model binding; analyst node; `ToolNode`; conditional routing and
return loop; streamed updates; system prompt; five live cases; allowlist and
missing-data errors; tool-call budget; two-turn checkpoint memory; final validator;
README and graph; the notebook's 16 planned learning sections.

The standard-library CSV reader and two extra state fields are small, documented
implementation choices. They do not expand the application beyond the plan.

1. **R1 — Important: live tool-failure recovery is not demonstrated.**
   The plan's section 17 asks to observe the LLM receiving a failed tool result
   and deciding what to do next. In `live_runs.json`, `missing_data` has no tool
   calls: the model answered from the capability descriptions. The direct tool
   exercises establish structured errors, and `test_tool_error_returns_to_model`
   establishes graph protocol with a scripted final message. Neither establishes
   a real model's response to a failed tool execution. This is an execution-evidence
   gap, not a missing error-return implementation.

2. **R2 — Minor: the worst-performer run makes redundant data calls.**
   Its first AI message requests three `get_country_data` calls and one
   `compare_metric` call together. The comparison already supplies the required
   values and ranking. The run uses five total tool calls where comparison plus
   search would supply the relevant evidence in two. The pure comparison case
   does select `compare_metric` directly. The issue is observed efficiency, not
   an invalid graph path.

3. **R3 — Minor: research conclusions are longer than the requested concise style.**
   The worst-performer answer includes a long list of explanations and repeats
   its comparison in the conclusion. The prompt requests concision, but no
   length maximum or section format enforces it. All answers can pass the current
   minimum-length validator regardless of verbosity.

### Layer 2 — System integrity

**ISSUES FOUND**

Architecture ownership is sound: Python owns CSV access, arithmetic, tool execution,
input checks and bounds; the model owns tool selection and synthesis. Tools and
graph orchestration live in separate modules. Earlier learning folders are
preserved. There is no UI or applicable visual design system.

4. **R4 — Minor: the earlier execution report overstates sequential decisions.**
   `results/RUN_REPORT.md` says the model made three retrieval calls “before
   compare_metric.” The actual trace puts all four calls in **the same AIMessage**.
   There is no intervening LLM observation between those requests, and their
   list order does not establish execution dependency. The subsequent search
   is a separate model decision after the batch returns. This distinction matters
   when teaching how an agent observes evidence and decides again. The new
   [learning notes](LEARNING_NOTES.md) and notebook review appendix explicitly
   clarify the trace; the original execution report remains as historical evidence.

### Layer 3 — Production readiness

**ISSUES FOUND**

5. **R5 — Important: the research answer mixes historical periods.**
   In the `research` run, one search snippet describes Germany's **2025** growth
   and export pressures, including higher US tariffs and a stronger euro. The
   final answer includes those factors in its explanation of **2024** without
   separating the periods. That same live page reports a revised 2024 figure
   different from the practice CSV; the answer does not explain the source-vintage
   difference. The CSV is correctly labeled illustrative, but that label does not
   cure a temporal mismatch in the explanation. The validator passes because
   it checks labels and URL presence, not historical scope or claim support.
   Evidence: `live_runs.json` → `research` → `web_search` result for
   `tradingeconomics.com/germany/full-year-gdp-growth`, and the corresponding
   final answer. This finding compares saved evidence with the saved answer;
   it is not a fresh assessment of Germany's economic statistics.

6. **R6 — Important: validation ignores evidence reused from earlier turns.**
   [analyst_graph.py:80](analyst_graph.py#L80) inspects only `current_turn(...)`,
   while the analyst receives the entire checkpointed history. A later answer
   can reuse earlier CSV figures without the practice-data label, or earlier
   search evidence without a URL, and these checks will not trigger if the later
   turn has no corresponding tool result. An offline probe retrieved practice
   inflation, then returned a longer follow-up containing `3.0%` with no label:
   validation still passed. The saved live memory follow-up happens to label its
   data; it does not exercise this gap. Evidence:
   [review_checks.json](results/review_checks.json) → `memory_validation`.

7. **R7 — Important: a failed validator does not make the CLI fail.**
   The runner stores and prints `validation`, but its final failure condition
   checks only `error_type` ([run_exercise.py:78](run_exercise.py#L78)). An offline
   CLI probe returned `Done.`, received `validation.passed = false`, and completed
   with exit code 0. A caller using exit status as its success signal cannot
   distinguish this from a passing answer. The validator is a reporting node,
   not an acceptance gate. Evidence:
   [review_checks.json](results/review_checks.json) → `cli_validation_failure`.

### Verification and boundaries of this review

- Reran all 10 existing offline tests: passed.
- Inspected all eight saved live runs, including tool names, arguments, results,
  final answers, and validation. Matched the reviewed CSV numbers and calculated
  differences/rankings to the returned tool evidence.
- Ran separate offline probes of cross-turn validation, CLI failure status and
  string-form search errors. The search error becomes a structured error as intended.
- Inspected installed `ToolNode` and `TavilySearch` behavior. In this environment,
  invocation errors can become tool messages, unexpected exceptions can propagate,
  and Tavily can internally convert some exceptions to an error result. The wrapper's
  lack of a blanket catch does not guarantee every underlying failure propagates.
- Reexecuted the annotated notebook: all 17 code cells completed without cell
  errors. Its default path reads saved live runs and executes local tools/tests;
  it does not rerun the entire live agent suite. A fresh live query is an explicit
  optional switch. The local Jupyter kernel emitted a warning about unencrypted
  TCP transport and a normal parent-exit shutdown warning. These concern the
  review execution environment; no public notebook service was tested.
- Did not repeat paid API calls or certify every external snippet/causal claim.
  Network outages, all model variants and long-running production sessions were
  not comprehensively tested.

The minimum-length, practice-label and URL-presence checks meet the plan's simple
validator scope. Numeric claim verification, source entailment and durable memory
were deliberately future work; they are limitations rather than omitted MVP features.

### Summary

**7 issues across 3 layers: 4 Important, 3 Minor, 0 Critical.**

Resolve the above before moving to the next feature, or explicitly decide which
limitations are acceptable for this learning MVP. No implementation fixes were
made during this review. The user's requested learning documentation was added.

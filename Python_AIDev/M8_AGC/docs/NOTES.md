# Module 8 Notes: AI Pair Programming Fundamentals

These notes align with the LMS progression through vibe coding, AI tool capabilities, Copilot context, iterative chat, generated-code quality, validation/testing, and prompt/context engineering. AI can accelerate execution, but the human and deterministic systems still own acceptance.

## 1. Human-owned development loop

A useful loop is:

1. define an observable outcome,
2. state constraints and non-goals,
3. provide only relevant context,
4. request a narrow change,
5. read the complete diff,
6. run deterministic checks,
7. report evidence and refine.

This is comparable to a controlled deployment workflow. A generated patch is a proposed mapping/job, not a successful production run.

## 2. Vibe coding: useful, with boundaries

**Vibe coding** means guiding implementation through natural-language intent and iteration. It can be efficient for scaffolding, transformations, and exploration.

Risks increase when:

- the requirement is ambiguous,
- the model invents APIs or repository facts,
- the task involves authorization/security,
- side effects are expensive or irreversible,
- a plausible answer replaces validation.

The human remains accountable for requirements, data boundaries, review, test results, and release decisions.

## 3. High-signal prompts

A coding prompt should name:

- **Outcome:** observable behavior.
- **Inputs/outputs:** schemas, examples, and edge cases.
- **Constraints:** compatibility, dependencies, performance, security.
- **Files/contracts:** relevant paths and public APIs.
- **Evidence:** exact validation command/tests.
- **Non-goals:** what must not be changed.

Weak:

```text
Make this code better.
```

Strong:

```text
Add rejection for blank customer IDs without changing the normalize_customer_id
return format. Use pytest, add one blank and one whitespace case, and run
python -m pytest -q tests/test_customers.py. Do not add dependencies.
```

The second prompt defines behavior and acceptance evidence.

## 4. Context engineering

Context is the information available to an assistant: conversation, selected files, repository structure, instructions, and tool results. More is not always better.

Prefer:

- smallest relevant code range,
- exact interface/contract,
- one representative success/failure example,
- project-specific instructions,
- command output for the actual failure.

Avoid:

- entire confidential repositories,
- credentials or production data,
- irrelevant history,
- duplicated documents,
- an answer in the prompt that prevents independent testing.

For a SQL/ETL specialist, context is like selecting only necessary source metadata and mapping parameters—not attaching every warehouse table to each job.

## 5. How Copilot-like tools add context

Tools may combine active edits, repository files, diagnostics, symbols/references, search, and conversation. Exact capabilities vary by environment, so do not assume a model saw a file unless the interface/tool confirms it.

Suggestions and generated explanations are hypotheses. Check:

- imports actually exist,
- symbols and signatures are correct,
- dependencies are declared,
- code matches selected Python version,
- behavior fits boundaries,
- security instructions were preserved.

## 6. Prompt patterns

Common patterns:

- **Zero-shot:** no example, only task and constraints.
- **One/few-shot:** representative input/output pairs.
- **Domain framing:** name the ETL/API/security context.
- **Structured output:** JSON schema or required sections.
- **Step-wise plan:** useful for long tasks, but steps still need execution evidence.
- **Critique/regenerate:** ask for review against explicit criteria.
- **Error-focused refinement:** include traceback, failing assertion, command, and expected behavior.

These are starting points, not guarantees. An example can accidentally narrow the solution too much or teach an incorrect pattern.

## 7. Generated-code review

Review the full diff, not just final lines:

- wrong requirement interpretation,
- invented APIs/packages,
- omitted error branches,
- off-by-one/index errors,
- insecure defaults,
- secret/data leakage,
- broad exception suppression,
- mutable/default state bugs,
- performance regressions,
- changes outside scope,
- missing migrations/docs,
- tests that mirror implementation rather than requirement.

Ask “What would have to be true for this patch to be correct?” Then gather evidence.

## 8. Validation ladder

Use increasingly strong evidence:

1. syntax parse,
2. linter/format/type diagnostics,
3. focused unit tests,
4. integration/contract tests,
5. end-to-end run,
6. manual review of security and data consequences.

Syntax only establishes parsability. A function can parse and still violate all requirements.

For an ETL change, inspect a clean sample, reject sample, duplicate, and downstream handoff. For an API, inspect status/body/side effect. For AI behavior, pin a deterministic provider mock before judging UI logic.

## 9. Tests generated by AI

A test is not automatically correct because it has `assert`.

Check that it:

- comes from an acceptance requirement,
- fails before the fix or catches a plausible regression,
- has meaningful input/output boundaries,
- avoids replicating implementation constants,
- asserts errors and side effects,
- uses deterministic data,
- remains independent of ordering/timing unless required.

Bad:

```python
assert normalize_customer_id("abc") == normalize_customer_id("abc")
```

Meaningful:

```python
assert normalize_customer_id("  ab-12 ") == "AB-12"
```

## 10. Security and privacy

Minimize data shared with AI tools. Never place secrets in examples, prompts, code, generated tests, or logs. Treat provider calls as data transfers subject to organizational policy.

Review generated code for:

- hard-coded credentials/tokens,
- `eval`/`exec`,
- shell interpolation / `shell=True`,
- disabled TLS verification,
- arbitrary paths/files,
- prompt injection boundaries,
- SSRF/unbounded network calls,
- authorization omissions,
- secret-bearing error details.

Automated scans are useful but incomplete. A suspicious literal may be false positive; an obfuscated secret can evade a simple pattern.

## 11. Dataclasses and callbacks in the harness

`Change` stores proposal inputs; `Finding` stores one gate result; `Gate` stores a named callback.

Building blocks:

- a **dataclass** reduces record-constructor boilerplate,
- `@dataclass(frozen=True)` prevents ordinary field assignment,
- `Callable[[Change], list[Finding]]` says “a function taking `Change` and returning findings,”
- `Gate.run()` invokes the configured check.

This makes quality rules replaceable and separately testable—composition rather than one large monolithic evaluator.

## 12. Gate design and limitations

The generated `ai_change_gate.py` has deterministic gates:

1. Python syntax for patch and tests,
2. possible credential literal scan,
3. risky construct scan,
4. acceptance-requirement evidence heuristic,
5. test function/assertion presence,
6. validation command recorded.

Expected default result:

```json
{
  "decision": "review",
  "errors": 0,
  "warnings": 0
}
```

`review` means “no deterministic errors,” not “approved.” The requirement gate is a keyword heuristic, so it cannot prove semantic test coverage. The syntax gate parses snippets but does not execute them. Real checks need the actual source and command environment.

## 13. Worked proposal

Proposal:

- requirement: reject blank identifier,
- summary: normalize a customer identifier,
- patch: strip/uppercase, then reject empty,
- tests: assert normalization and `pytest.raises(ValueError)`.

Trace:

1. `ast.parse` accepts patch/test syntax.
2. secret and unsafe regular checks do not match.
3. requirement keywords appear in summary/tests.
4. test file shape contains tests and assertions.
5. validation command exists.
6. no gate errors → human review.

Important: the gate does not prove the proposed snippets run together. Execute the actual pytest command in the actual repository.

## 14. Iterative refinement

If a model's result is weak, send evidence rather than “try again”:

```text
The test fails with TypeError at customer.py:17 because provider_id is None.
Expected behavior for None is ValueError according to requirement R3.
Keep the signature and existing successful behavior unchanged.
```

This tells the assistant the observed value, exact contract, and boundary. Keep each iteration reviewable and rerun the narrow validation.

## 15. Human review for scheduler/ETL changes

For an AutoSys/Informatica migration analogy, verify:

- startup and exit codes,
- idempotent rerun behavior,
- checkpoint/recovery semantics,
- reject records,
- source/target schema,
- time zones and calendars,
- credentials through approved secret stores,
- concurrency/locks,
- data retention and auditability.

These concerns are requirements, not something an AI completion can infer safely.

## 16. Debugging/checklist

1. Preserve original error and exact command.
2. Verify current branch/worktree and changed files.
3. Read every diff hunk.
4. Check declared dependencies and versions.
5. Run focused validation with representative inputs.
6. Ensure tests fail on the wrong behavior.
7. Search for sensitive output and broad suppressions.
8. Confirm backward-compatible/public-contract behavior.
9. Record commands and results.
10. Ask a human/domain reviewer for unresolved risk.

## 17. Common mistakes

- Sharing an entire confidential repo when only one interface matters.
- Accepting a “looks good” summary as a test.
- Letting generated tests dictate requirements after the fact.
- Running only formatting and calling the task complete.
- Assuming a warning-free scanner means secure.
- Using one giant prompt for unrelated changes.
- Accepting dependency additions without review.
- Treating human review as unnecessary after AI review.

## 18. Practice

1. Rewrite a vague request into outcome/constraints/evidence/non-goals.
2. Create a positive and negative proposal for the quality gate.
3. Add a security gate for disabled TLS verification and test positive/negative strings.
4. Add a requirement-to-test mapping field rather than a keyword heuristic.
5. Make a test intentionally fail; provide the exact error as iterative context.
6. Review a ten-line patch for invented API, missing edge case, and secret exposure.
7. Compare “scanner says pass,” focused pytest, and end-to-end run in a short evidence table.
8. State the human decision and remaining risks even after all gates pass.

## 19. LMS demonstration walkthrough

**Exact resources:** [setup 15496](https://lms.snvaveranda.com/mod/resource/view.php?id=15496), [generation/refactoring 15497](https://lms.snvaveranda.com/mod/resource/view.php?id=15497), [unit testing 15498](https://lms.snvaveranda.com/mod/resource/view.php?id=15498), and [advanced prompting 15499](https://lms.snvaveranda.com/mod/resource/view.php?id=15499).

### Actual scenario and data

The first demonstration verifies Copilot account/VS Code authorization, inline completion, and chat. The second generates an average-over-list function and refactors a deliberately repetitive customer formatter. The third creates a price validator and reviews/generated pytest coverage, including investigating an incorrect expectation. The fourth compares vague and structured prompting while refining a small order-pricing contract.

Use only original records:

```text
numbers = [10, 13, 17]
customer = {"name":"Sample", "email":"person@example.invalid", "city":"Testville"}
items = [{"price":25.0, "quantity":2}]
```

The schemas are ordinary in-memory Python values; no dataset or provider key is required. All acceptance behavior must be stated independently of the generated code.

### Step-by-step beginner workflow

1. Sign in and confirm both Chat and an inline suggestion; do not continue if the development environment is not authenticated.
2. In a tiny file, describe expected behavior and one edge case before asking for code.
3. Review every generated line. In particular, verify empty input, rounding, and exception behavior rather than accepting plausible output.
4. Run the function with the predicted case; then use selected-code inline chat for one narrow readability refactor.
5. Confirm behavior before and after the refactor. Reject unrelated changes.
6. Ask for price tests by requirement (valid, boundary, invalid) and run pytest before judging coverage.
7. Add one deliberately wrong expectation, read the assertion, then ask Copilot to explain the failure without changing production behavior.
8. For the pricing scenario, compare a vague prompt with role/context/task/constraints/output. Use focused selection and follow-up prompts.
9. Read the diff, rerun focused tests, and record what deterministic evidence does not prove.

### Connection to the current examples

`ai_change_gate.py` is an **original extension beyond the LMS demonstrations**. It organizes proposal text, snippets, tests, and validation into explainable heuristic gates. It does not call Copilot, run the proposed patch in the repository, or certify correctness. Passing its deterministic checks still requires actual pytest/execution and human requirement review.

### Deliberate practice

Write a requirement table before prompting: empty list, negative price, zero quantity, and total calculation. Compare what a vague request and a structured request miss. Ask for a risk list first, then a one-function refactor, then focused tests. Introduce an intentionally incorrect expected result and use the failure output to resolve the disagreement. Finish with a diff checklist and name at least one risk that successful tests do not eliminate.

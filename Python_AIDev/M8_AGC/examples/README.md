# AI change quality gate

`ai_change_gate.py` turns an AI-assisted change description, patch, tests, acceptance requirements, and recorded validation into an explainable report. It does not call Copilot or any model. It demonstrates deterministic syntax, secret, unsafe-pattern, requirement-evidence, assertion, and validation gates.

```bash
python ai_change_gate.py
python ai_change_gate.py --input proposal.json --output report.json
```

The default proposal should receive `decision: review` with no errors or warnings. Missing tests, malformed Python, a credential literal, or unsafe constructs block a proposal. Warnings identify evidence gaps that still need human review; a “review” decision is not approval.

Challenges: parse actual unified-diff headers, map tests to requirements structurally, add a dependency-license rule, reject debug prints, compare a proposal with executed command results, and add pytest tests for every rule.

## LMS bridge

Pair the four LMS resources 15496–15499 with this example: verify setup, generate/refactor one tiny function, request focused pytest cases, and practice structured/follow-up prompts. Use your own synthetic records and review every suggestion. This gate is an original extension: it neither invokes Copilot nor certifies generated work, so retain the LMS requirement to run code/tests and make the final human decision.

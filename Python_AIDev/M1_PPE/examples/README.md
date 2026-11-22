# Course workspace planner

`course_workspace_planner.py` converts validated course specifications into a deterministic folder plan. It demonstrates immutable records, collections, validation, precedence, f-strings, path values, JSON, and a safe dry-run mode.

## Run

From this directory:

```bash
python course_workspace_planner.py
python course_workspace_planner.py --root generated_workspace --apply
```

The default run prints the plan and changes nothing. `--apply` creates the directories. A JSON file may be supplied with `--json` as an array containing `slug`, `lessons`, and optional `assets`.

## Expected behavior

The summary reports five lesson plans, 12 directories, sorted output, and no filesystem changes in dry-run mode. Invalid slugs, duplicate assets, duplicate courses, invalid lesson counts, or excessive plans exit with code 2 and a concise error.

## Extension challenges

1. Add `duration_minutes` and compute expected production hours.
2. Detect an existing workspace and produce a change report.
3. Add optional `--format csv`.
4. Write focused tests for aliases, invalid booleans, and boundary lesson counts.

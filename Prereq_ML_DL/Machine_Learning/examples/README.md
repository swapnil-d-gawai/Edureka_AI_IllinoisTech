# Machine Learning Example

`churn_pipeline.py` is an offline, deterministic demonstration requiring only
NumPy. It generates customer snapshots, performs customer-level train,
validation, and test splits, fits preprocessing only on training data, compares
logistic regression with a small tree ensemble, tunes the decision threshold
on validation data, and reports test metrics plus transparent fairness slices.

Run from the repository root:

```bash
./venv/bin/python Prereq_ML_DL/Machine_Learning/examples/churn_pipeline.py
```

The output is educational, not a production benchmark. The intentionally
sensitive `region` field is excluded from model inputs; it is used only for a
post-hoc slice audit. No network, paid service, external dataset, or generated
artifact is required.

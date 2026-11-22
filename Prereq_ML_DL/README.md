# Pre-Requisite: Machine Learning and Deep Learning

LMS course: [Machine Learning and Deep Learning](https://lms.snvaveranda.com/course/view.php?id=266)

The LMS course has two sections. Each has eight video recordings and no
published presentation deck:

- [Machine_Learning](Machine_Learning/docs/README.md) — classical ML,
  evaluation, deployment, and a leakage-aware churn workflow
- [Deep_Learning](Deep_Learning/docs/README.md) — network mechanics,
  architectures, and a NumPy MLP trained from backpropagation

This material is designed for a learner experienced with SQL, Informatica,
Unix, AutoSys, or IBM TWS. ML and DL vocabulary is introduced gradually and
connected to familiar ideas such as transformations, joins, validation,
scheduling, reconciliation, and batch monitoring.

## Study workflow

1. Read a note section before opening its corresponding example.
2. Map the input, transformations, validation, and output to an ETL job.
3. Start with the ML notes and recordings, then run its offline churn example.
4. Continue with the DL notes and recordings, then run the NumPy MLP.
5. Predict what will happen before execution, inspect the metrics, and change
   one parameter at a time.
6. Record assumptions, selected thresholds/checkpoints, failure modes, and a
   monitoring plan rather than optimizing a single score.
7. Complete both with a compact model card and inference checklist. The
   exercises run with NumPy; the current workspace does not require pandas,
   scikit-learn, or PyTorch.

Module notes and recording indexes are in each `docs` folder; runnable
instructions and examples are in each `examples` folder.

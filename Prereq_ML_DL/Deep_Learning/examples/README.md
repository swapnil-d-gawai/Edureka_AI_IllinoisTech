# Deep Learning Example

`numpy_binary_mlp.py` is an offline binary-classification implementation using
only NumPy. It constructs a small nonlinear dataset, standardizes from training
statistics, trains a two-hidden-layer MLP with manual backpropagation and Adam,
uses L2 regularization and validation early stopping, restores the best weights,
and reports train, validation, and test metrics.

Run from the repository root:

```bash
./venv/bin/python Prereq_ML_DL/Deep_Learning/examples/numpy_binary_mlp.py
```

The implementation is intentionally compact enough to study line by line. It
demonstrates the mechanics behind a framework loop; it does not replace mature
autograd and production tooling. It needs no external dataset, network, paid
service, or generated artifact.

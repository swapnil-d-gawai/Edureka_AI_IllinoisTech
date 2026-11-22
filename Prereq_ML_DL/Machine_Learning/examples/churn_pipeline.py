"""Leakage-aware tabular churn workflow implemented with NumPy only."""

from __future__ import annotations

import numpy as np

SEED = 7


def sigmoid(values: np.ndarray) -> np.ndarray:
    # Clipping prevents extreme scores from overflowing exp(-values), without
    # changing the useful probability range for normal model inputs.
    clipped = np.clip(values, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def make_customers(n: int = 2400) -> tuple[dict[str, np.ndarray], np.ndarray]:
    # Fixed randomness makes this teaching run reproducible, like rerunning a
    # sample load from the same source snapshot.
    rng = np.random.default_rng(SEED)
    customer_id = np.arange(n)
    region = rng.integers(0, 3, n)
    tenure = np.clip(rng.gamma(2.4, 11.0, n), 1.0, 84.0)
    monthly_charges = np.clip(rng.normal(67 + region * 2, 18, n), 18, 145)
    support_tickets = rng.poisson(0.35 + monthly_charges / 130, n)
    contract = rng.choice(["month", "annual"], n, p=[0.66, 0.34])
    usage_drop = np.clip(rng.normal(0.0, 0.22, n) - 0.1 * (tenure < 10), -0.8, 0.9)
    # Build a plausible churn signal from features plus irreducible noise.
    # The model must learn these effects from rows; this formula is not exposed
    # as a feature during preprocessing or prediction.
    logit = (
        -2.30
        - 0.027 * tenure
        + 0.021 * monthly_charges
        + 0.36 * support_tickets
        + 1.20 * (contract == "month")
        + 1.75 * usage_drop
        + rng.normal(0, 0.55, n)
    )
    probability = sigmoid(logit)
    label = (rng.random(n) < probability).astype(int)
    # This post-outcome column is deliberately supplied but never selected:
    # using it would resemble joining cancellation results into a pre-churn
    # extract. The comments and output make the leakage trap visible.
    data = {
        "customer_id": customer_id,
        "region": region,
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "support_tickets": support_tickets,
        "contract": contract,
        "usage_drop": usage_drop,
        "refund_after_cancellation": np.where(
            label, rng.normal(80, 8, n), rng.normal(3, 2, n)
        ),
    }
    return data, label


def group_split(
    ids: np.ndarray, train_fraction: float = 0.6, validation_fraction: float = 0.2
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    order = np.random.default_rng(SEED).permutation(len(ids))
    train_end = int(train_fraction * len(ids))
    validation_end = train_end + int(validation_fraction * len(ids))
    return order[:train_end], order[train_end:validation_end], order[validation_end:]


class Preprocessor:
    """Training-only median/standardization and fixed categorical vocabulary."""

    numeric = ("tenure", "monthly_charges", "support_tickets", "usage_drop")

    def fit(self, data: dict[str, np.ndarray], rows: np.ndarray) -> "Preprocessor":
        # Fit every learned transform on train rows only. These saved values are
        # part of the deployable model artifact, just like a lookup cache.
        matrix = np.column_stack([data[name][rows] for name in self.numeric])
        self.median = np.nanmedian(matrix, axis=0)
        filled = np.where(np.isfinite(matrix), matrix, self.median)
        self.mean = filled.mean(axis=0)
        self.scale = filled.std(axis=0)
        self.scale[self.scale == 0] = 1.0
        self.contracts = ("month", "annual")
        return self

    def transform(self, data: dict[str, np.ndarray], rows: np.ndarray) -> np.ndarray:
        numeric = np.column_stack([data[name][rows] for name in self.numeric])
        numeric = np.where(np.isfinite(numeric), numeric, self.median)
        # Reuse the training mean/scale; never refit them on validation,
        # test, or an incoming production micro-batch.
        numeric = (numeric - self.mean) / self.scale
        contract = data["contract"][rows]
        # A two-category fixed vocabulary creates two explicit indicator fields.
        # A real service also needs an intentional unknown-category policy.
        one_hot = np.column_stack([contract == value for value in self.contracts])
        return np.column_stack([numeric, one_hot]).astype(float)


class LogisticRegression:
    def __init__(self, learning_rate: float = 0.08, epochs: int = 900, l2: float = 0.02):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.l2 = l2

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LogisticRegression":
        # Start with neutral weights and repeatedly follow the average training
        # loss gradient. Matrix multiplication evaluates all rows together.
        self.weights = np.zeros(x.shape[1])
        self.bias = 0.0
        for _ in range(self.epochs):
            probability = sigmoid(x @ self.weights + self.bias)
            error = probability - y
            # Divide by row count to make the update batch-size independent;
            # add L2's gradient to discourage needlessly large coefficients.
            self.weights -= self.learning_rate * (
                x.T @ error / len(y) + self.l2 * self.weights
            )
            self.bias -= self.learning_rate * error.mean()
        return self

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        return sigmoid(x @ self.weights + self.bias)


class Tree:
    """Shallow, greedy CART tree for continuous (already transformed) features."""

    def __init__(self, max_depth: int = 4, min_leaf: int = 25):
        self.max_depth = max_depth
        self.min_leaf = min_leaf
        self.root: dict[str, object] | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "Tree":
        rng = np.random.default_rng(SEED + len(y))
        features = np.arange(x.shape[1])
        self.root = self._grow(x, y, 0, features, rng)
        return self

    def _grow(
        self, x: np.ndarray, y: np.ndarray, depth: int, features: np.ndarray, rng: np.random.Generator
    ) -> dict[str, object]:
        # A leaf predicts the observed positive rate for rows reaching it.
        probability = float(np.mean(y))
        node: dict[str, object] = {"probability": probability}
        if depth >= self.max_depth or len(y) < 2 * self.min_leaf or y.min() == y.max():
            return node
        # Random feature candidates decorrelate trees in the small forest.
        candidates = rng.choice(features, size=max(1, int(np.sqrt(len(features)))), replace=False)
        best: tuple[float, int, float] | None = None
        for feature in candidates:
            values = np.unique(x[:, feature])
            if len(values) > 40:
                values = np.quantile(values, np.linspace(0.05, 0.95, 30))
            for threshold in values:
                left = x[:, feature] <= threshold
                n_left = int(left.sum())
                if n_left < self.min_leaf or len(y) - n_left < self.min_leaf:
                    continue
                left_rate = float(y[left].mean())
                right_rate = float(y[~left].mean())
                impurity = (
                    n_left * 2 * left_rate * (1 - left_rate)
                    + (len(y) - n_left) * 2 * right_rate * (1 - right_rate)
                ) / len(y)
                parent = 2 * probability * (1 - probability)
                gain = parent - impurity
                # Pick the threshold with the largest reduction in weighted
                # impurity, subject to the minimum leaf-size guard above.
                if best is None or gain > best[0]:
                    best = (gain, int(feature), float(threshold))
        if best is None or best[0] <= 1e-9:
            return node
        _, feature, threshold = best
        left = x[:, feature] <= threshold
        # Recursion builds child routing nodes until the stopping conditions
        # turn a child into a prediction leaf.
        node.update(
            {
                "feature": feature,
                "threshold": threshold,
                "left": self._grow(x[left], y[left], depth + 1, features, rng),
                "right": self._grow(x[~left], y[~left], depth + 1, features, rng),
            }
        )
        return node

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        assert self.root is not None

        def predict_one(row: np.ndarray) -> float:
            node = self.root
            assert node is not None
            # Follow the learned if/else path until reaching a probability leaf.
            while "feature" in node:
                branch = "left" if row[int(node["feature"])] <= float(node["threshold"]) else "right"
                node = node[branch]  # type: ignore[assignment]
            return float(node["probability"])

        return np.array([predict_one(row) for row in x])


class RandomForestLite:
    def __init__(self, trees: int = 35, max_depth: int = 5):
        self.tree_count = trees
        self.max_depth = max_depth

    def fit(self, x: np.ndarray, y: np.ndarray) -> "RandomForestLite":
        rng = np.random.default_rng(SEED)
        self.trees = []
        for _ in range(self.tree_count):
            # A bootstrap sample is training rows sampled with replacement.
            # Each tree therefore sees a slightly different data partition.
            rows = rng.integers(0, len(y), len(y))
            self.trees.append(Tree(self.max_depth, min_leaf=18).fit(x[rows], y[rows]))
        return self

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        # Averaging weakly correlated tree estimates reduces variance.
        return np.mean([tree.predict_proba(x) for tree in self.trees], axis=0)


def metrics(y: np.ndarray, probability: np.ndarray, threshold: float) -> dict[str, float]:
    # Thresholding is where a probability score becomes an operational action.
    predicted = probability >= threshold
    positive = y == 1
    tp = int((predicted & positive).sum())
    fp = int((predicted & ~positive).sum())
    tn = int((~predicted & ~positive).sum())
    fn = int((~predicted & positive).sum())
    # max(..., 1) avoids a division error if a metric has no qualifying rows.
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    specificity = tn / max(tn + fp, 1)
    return {
        "accuracy": (tp + tn) / len(y),
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-12),
        "balanced_accuracy": (recall + specificity) / 2,
        "selection_rate": float(predicted.mean()),
    }


def choose_threshold(y: np.ndarray, probability: np.ndarray) -> float:
    # Threshold candidates are development settings, so this function receives
    # validation outcomes only in main(). The objective is a business-shaped
    # "maximize recall while retaining a useful precision" constraint.
    thresholds = np.linspace(0.15, 0.75, 61)
    # Maximize recall while retaining at least 55% precision on validation.
    choices = [(metrics(y, probability, t)["recall"], t) for t in thresholds
               if metrics(y, probability, t)["precision"] >= 0.55]
    return float(max(choices, default=(0.0, 0.5))[1])


def main() -> None:
    data, target = make_customers()
    train, validation, test = group_split(data["customer_id"])
    # Fail fast if a future split implementation leaks rows across partitions.
    assert set(train).isdisjoint(test) and set(validation).isdisjoint(train)
    # The fitted preprocessor is one shared state object used without refitting.
    prep = Preprocessor().fit(data, train)
    x_train, x_validation, x_test = (
        prep.transform(data, rows) for rows in (train, validation, test)
    )

    models = {
        # Keep a transparent linear baseline beside the stronger ensemble.
        "logistic_baseline": LogisticRegression().fit(x_train, target[train]),
        "tree_ensemble": RandomForestLite().fit(x_train, target[train]),
    }
    validation_scores: dict[str, tuple[float, float]] = {}
    for name, model in models.items():
        probability = model.predict_proba(x_validation)
        # Select the operating threshold and model using validation only.
        threshold = choose_threshold(target[validation], probability)
        validation_scores[name] = (
            metrics(target[validation], probability, threshold)["balanced_accuracy"],
            threshold,
        )
        print(f"{name:20s} validation={metrics(target[validation], probability, threshold)}")
    winner = max(validation_scores, key=lambda name: validation_scores[name][0])
    threshold = validation_scores[winner][1]
    test_probability = models[winner].predict_proba(x_test)
    # This is the single final report at the previously frozen model/threshold.
    print(f"\nSelected model: {winner}; threshold from validation only: {threshold:.3f}")
    print(f"Test metrics: {metrics(target[test], test_probability, threshold)}")
    print("Test region slices (post-hoc audit; region was not a model feature):")
    # Slices can expose unequal performance hidden by a single aggregate score.
    for region in range(3):
        rows = np.flatnonzero(data["region"][test] == region)
        print(
            f"  region={region} n={len(rows):3d}: "
            f"{metrics(target[test][rows], test_probability[rows], threshold)}"
        )
    print(
        "\nLeakage guard: refund_after_cancellation is omitted because it is "
        "observed after cancellation."
    )


if __name__ == "__main__":
    main()

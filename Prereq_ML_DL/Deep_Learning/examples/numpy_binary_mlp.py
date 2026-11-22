"""A small binary MLP with manual backpropagation, Adam, and early stopping."""

from __future__ import annotations

import numpy as np

SEED = 11


def sigmoid(x: np.ndarray) -> np.ndarray:
    # Stable sigmoid for probabilities: clip only the exponential input.
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))


def make_data(n: int = 1800) -> tuple[np.ndarray, np.ndarray]:
    # Deterministic synthetic records let a learner focus on network mechanics.
    rng = np.random.default_rng(SEED)
    features = rng.normal(size=(n, 6))
    # The interaction and squared term make a plain linear rule insufficient.
    # Feature 5 is intentionally unused noise, as is common in real extracts.
    nonlinear = (
        1.15 * features[:, 0] * features[:, 1]
        - 0.85 * features[:, 2]
        + 0.65 * features[:, 3] ** 2
        - 0.35 * features[:, 4]
    )
    probability = sigmoid(nonlinear - 0.15 + rng.normal(0, 0.12, n))
    labels = (rng.random(n) < probability).astype(float)
    return features, labels


def split(
    x: np.ndarray, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # The example has independent synthetic rows, so a shuffled 60/20/20 split
    # is appropriate. Production time/entity correlation may require a
    # chronological or grouped split instead.
    rows = np.random.default_rng(SEED).permutation(len(y))
    train, validation, test = rows[:1080], rows[1080:1440], rows[1440:]
    return x[train], y[train], x[validation], y[validation], x[test], y[test]


class MLP:
    def __init__(self, sizes: tuple[int, ...], learning_rate: float = 0.012, l2: float = 0.001):
        rng = np.random.default_rng(SEED)
        # A matrix for each edge between layer widths performs one dense stage.
        # He-style scaling helps keep ReLU activations in a useful range.
        self.weights = [
            rng.normal(0, np.sqrt(2 / fan_in), (fan_in, fan_out))
            for fan_in, fan_out in zip(sizes[:-1], sizes[1:])
        ]
        self.biases = [np.zeros((1, width)) for width in sizes[1:]]
        self.learning_rate = learning_rate
        self.l2 = l2
        # Adam needs one running first and second moment for every parameter.
        self.first_moment = [np.zeros_like(value) for pair in zip(self.weights, self.biases) for value in pair]
        self.second_moment = [np.zeros_like(value) for pair in zip(self.weights, self.biases) for value in pair]
        self.step = 0

    def parameters(self) -> list[np.ndarray]:
        # Keep one explicit order: weight, bias, weight, bias, ...
        # Gradients and Adam state must use this exact same order.
        return [value for pair in zip(self.weights, self.biases) for value in pair]

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
        # Cache both pre- and post-activation values for the backward chain rule.
        activations = [x]
        preactivations: list[np.ndarray] = []
        for index, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            z = activations[-1] @ weight + bias
            preactivations.append(z)
            # Hidden layers use ReLU; the last layer intentionally returns a raw
            # binary logit rather than an already-sigmoided probability.
            activations.append(np.maximum(0.0, z) if index < len(self.weights) - 1 else z)
        return activations[-1], activations, preactivations

    def loss(self, x: np.ndarray, y: np.ndarray) -> float:
        logits, _, _ = self.forward(x)
        target = y[:, None]
        # This log-sum-exp form is binary cross-entropy without unstable logs
        # of a rounded probability 0 or 1.
        data_loss = np.logaddexp(0.0, logits) - target * logits
        # L2 is a training-only penalty and is omitted from prediction metrics.
        penalty = self.l2 * sum(float((weight * weight).sum()) for weight in self.weights)
        return float(data_loss.mean() + penalty)

    def backward(
        self, activations: list[np.ndarray], preactivations: list[np.ndarray], y: np.ndarray
    ) -> list[np.ndarray]:
        # For sigmoid plus binary cross-entropy, the final delta simplifies to
        # (prediction - target). Dividing now yields per-example gradients.
        delta = (sigmoid(preactivations[-1]) - y[:, None]) / len(y)
        weight_gradients: list[np.ndarray] = [np.empty_like(w) for w in self.weights]
        bias_gradients: list[np.ndarray] = [np.empty_like(b) for b in self.biases]
        # Walk layer order in reverse, using each cached forward-stage shape.
        for layer in range(len(self.weights) - 1, -1, -1):
            # Weight gradient plus the derivative of the L2 penalty.
            weight_gradients[layer] = activations[layer].T @ delta + 2 * self.l2 * self.weights[layer]
            bias_gradients[layer] = delta.sum(axis=0, keepdims=True)
            if layer:
                # Propagate sensitivity left, then apply ReLU's 0/1 derivative.
                delta = (delta @ self.weights[layer].T) * (preactivations[layer - 1] > 0)
        return [value for pair in zip(weight_gradients, bias_gradients) for value in pair]

    def adam_step(self, gradients: list[np.ndarray]) -> None:
        self.step += 1
        beta1, beta2, epsilon = 0.9, 0.999, 1e-8
        for parameter, gradient, m, v in zip(
            self.parameters(), gradients, self.first_moment, self.second_moment
        ):
            # Exponential moving means of gradient and squared gradient smooth
            # updates and adapt their scale per parameter.
            m *= beta1
            m += (1 - beta1) * gradient
            v *= beta2
            v += (1 - beta2) * gradient * gradient
            m_hat = m / (1 - beta1**self.step)
            v_hat = v / (1 - beta2**self.step)
            # epsilon prevents division by zero near a flat parameter.
            parameter -= self.learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)

    def train_batch(self, x: np.ndarray, y: np.ndarray) -> None:
        # One mini-batch cycle: forward computation -> gradients -> Adam update.
        _, activations, preactivations = self.forward(x)
        self.adam_step(self.backward(activations, preactivations, y))

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        logits, _, _ = self.forward(x)
        return sigmoid(logits[:, 0])

    def snapshot(self) -> tuple[list[np.ndarray], list[np.ndarray]]:
        # Copies are essential: a reference to live arrays would change when
        # later epochs update the model and would not preserve the checkpoint.
        return ([w.copy() for w in self.weights], [b.copy() for b in self.biases])

    def restore(self, state: tuple[list[np.ndarray], list[np.ndarray]]) -> None:
        self.weights = [w.copy() for w in state[0]]
        self.biases = [b.copy() for b in state[1]]


def metrics(y: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    # A fixed 0.5 threshold makes the learning loop easy to read. In a real
    # decision workflow, validation outcomes should select this threshold too.
    predicted = probability >= 0.5
    tp = int((predicted & (y == 1)).sum())
    fp = int((predicted & (y == 0)).sum())
    tn = int((~predicted & (y == 0)).sum())
    fn = int((~predicted & (y == 1)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    loss = -np.mean(y * np.log(probability + 1e-12) + (1 - y) * np.log(1 - probability + 1e-12))
    return {
        "loss": float(loss),
        "accuracy": (tp + tn) / len(y),
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-12),
    }


def main() -> None:
    x, y = make_data()
    x_train, y_train, x_validation, y_validation, x_test, y_test = split(x, y)
    # Learn scaling state from train only and treat it as inference metadata.
    mean, scale = x_train.mean(axis=0), x_train.std(axis=0)
    scale[scale == 0] = 1.0
    x_train = (x_train - mean) / scale
    x_validation = (x_validation - mean) / scale
    x_test = (x_test - mean) / scale

    model = MLP((x.shape[1], 24, 12, 1))
    # Early stopping compares the independent holdout against a best snapshot;
    # it is separate from optimizer training and therefore uses validation.
    best_loss = float("inf")
    best_epoch = 0
    best_state = model.snapshot()
    patience = 12
    stale_epochs = 0
    rng = np.random.default_rng(SEED)
    for epoch in range(1, 151):
        # Each array_split produces one mini-batch; shuffle differs each epoch
        # but remains deterministic because the generator state is fixed.
        for rows in np.array_split(rng.permutation(len(y_train)), 24):
            model.train_batch(x_train[rows], y_train[rows])
        validation_loss = model.loss(x_validation, y_validation)
        if validation_loss < best_loss - 1e-4:
            # Preserve copies at the first stable new best, and reset patience.
            best_loss, best_epoch = validation_loss, epoch
            best_state, stale_epochs = model.snapshot(), 0
        else:
            stale_epochs += 1
        if epoch in (1, 5, 10, 25) or stale_epochs == 0:
            print(
                f"epoch={epoch:3d} train_loss={model.loss(x_train, y_train):.4f} "
                f"validation_loss={validation_loss:.4f}"
            )
        if stale_epochs >= patience:
            print(f"Early stopping at epoch {epoch}; patience={patience}.")
            break

    model.restore(best_state)
    # Final test reporting uses the selected checkpoint and never changes it.
    print(f"\nRestored best checkpoint from epoch {best_epoch}.")
    for label, features, target in (
        ("train", x_train, y_train),
        ("validation", x_validation, y_validation),
        ("test", x_test, y_test),
    ):
        print(f"{label:10s} {metrics(target, model.predict_proba(features))}")
    print(
        "\nAt inference, keep model training mode disabled conceptually, use the "
        "saved training mean/scale, and never refit on incoming records."
    )


if __name__ == "__main__":
    main()

# Deep Learning for a Data-Pipeline Developer

## 1. What "deep" means

**Deep learning (DL)** is a branch of machine learning in which models use
multiple learned layers to turn inputs into predictions. Classical tabular ML
often relies on carefully engineered columns and models such as logistic
regression or trees. Deep learning can learn intermediate **representations**
from data, which is a model-created encoding of patterns rather than a
manually defined warehouse dimension.

"Deep" does not mean automatically better. It means the forward computation
passes through multiple trainable transformations. It usually adds more
parameters, data requirements, compute, tuning, and failure modes. On structured
tabular data, a well-validated tree or logistic model may be simpler and
better.

### First vocabulary

- **Tensor:** an n-dimensional array. A scalar is rank 0, vector rank 1,
  matrix rank 2, and higher-rank arrays represent images, sequences, and
  batches.
- **Shape:** the number of values in each dimension, such as `(120, 6)` for 120
  rows and 6 features.
- **Batch:** the subset processed in one model update, analogous to a
  processing partition.
- **Epoch:** one pass over the training rows. With 1,080 rows and batches of
  45, an epoch contains 24 update steps.
- **Parameter/weight:** a number the optimizer changes to reduce loss.
- **Forward pass:** compute layer outputs and loss.
- **Loss:** a scalar measure of prediction error. The optimization process
  tries to reduce it.
- **Gradient:** the derivative showing how loss changes if each parameter
  changes.
- **Backward pass/backpropagation:** use calculus and the chain rule to
  calculate all parameter gradients layer by layer.
- **Optimizer:** the update algorithm, such as Adam, that applies gradients.
- **Inference:** run the fixed trained model on new records.

## 2. A network as a staged mapping

Think of a dense neural network as an Informatica mapping with many
configurable transformations whose coefficients were learned:

```text
6 input columns -> 24 hidden units -> 12 hidden units -> 1 logit
```

In the example, the first layer has a `6 x 24` weight matrix. Each of the 24
hidden units calculates:

`output = input row @ 24 weights + bias`, then applies an activation.

A later layer transforms those 24 values into 12 values, and the final layer
transforms 12 values into one raw binary score, called a **logit**. The logit
is converted by sigmoid to a probability during evaluation.

### Tiny matrix walkthrough

Imagine one row `x = [2, 3]` and a one-output layer:

- weights = `[0.5, -1.0]`
- bias = `0.2`
- logit = `2(0.5) + 3(-1.0) + 0.2 = -1.8`
- sigmoid(-1.8) is about `0.142`

The model estimates a 14.2% probability for this row. A second layer would use
many such intermediate values instead of the original row.

### Activation functions

An **activation** is a nonlinear function after a layer. Without nonlinear
activations, stacked linear transformations collapse to one linear mapping.

- **ReLU:** `max(0, z)`. If z is negative, output is zero; otherwise z.
  It is common in hidden layers and is used in the example.
- **Sigmoid:** maps a real score to `(0, 1)`. It is appropriate for a binary
  output probability, but can saturate in deep hidden layers.
- **Tanh:** maps to `(-1, 1)` and is zero-centered, but can also saturate.
- **Softmax:** turns multiple class logits into class probabilities that sum
  to one.

Final activation and loss are a matched contract. The example's final layer
returns one raw logit and uses binary cross-entropy/logistic loss. It does
not put sigmoid inside the loss because `logaddexp` computes the stable
equivalent.

## 3. Shapes are schema

Shape errors in neural networks are like joins with the wrong grain. Values
may have the correct type yet the operation's meaning is invalid.

For a batch of 45 examples:

```text
x                         (45, 6)
first weight              (6, 24)
first preactivation       (45, 24)
second weight             (24, 12)
second preactivation      (45, 12)
final weight              (12, 1)
final logit               (45, 1)
labels after y[:, None]   (45, 1)
```

The code adds a dimension to labels because `(45,)` and `(45, 1)` should not
be left to accidental broadcasting. Broadcasting can be useful, but silent
broadcasting across semantically different axes is dangerous.

For production data, validate:

- exact row width and feature order;
- expected dtype and finite values;
- units (dollars versus thousands, milliseconds versus seconds);
- image channel convention or sequence padding if applicable;
- batch behavior on one row as well as a full batch.

## 4. Why the synthetic problem needs a network

`make_data` creates six standard-normal columns and a nonlinear relationship:

```text
signal =
  1.15 * feature_0 * feature_1
- 0.85 * feature_2
+ 0.65 * feature_3 squared
- 0.35 * feature_4
```

Feature 5 is effectively noise. The label is sampled with probability
`sigmoid(signal - 0.15 + noise)`, not calculated as a deterministic simple
rule. The model therefore cannot expect 100% accuracy.

The interaction `feature_0 * feature_1` and squared `feature_3` cannot be
represented as one plain linear sum without engineered features. Hidden
nonlinear layers can approximate those relationships.

## 5. Split and preprocessing walk-through

The 1,800 rows are divided deterministically:

- train: 1,080 (60%)
- validation: 360 (20%)
- test: 360 (20%)

As in classical ML:

- train is for fitting mean/scale and parameters;
- validation is for checkpoint and early-stopping decisions;
- test is used once for the final estimate.

The preprocessing lines calculate each training column's mean and standard
deviation, then apply those saved values to all splits:

```text
standardized = (raw - training_mean) / training_scale
```

If one training feature is constant, division would fail or create extreme
values. The example sets a zero standard deviation to `1.0`.

Never compute a production batch's own mean and scale for inference. Two
identical customer rows could otherwise receive different model inputs
depending on the other records in their batch.

## 6. Training loop as an orchestration job

The NumPy loop is a deliberately transparent version of a framework loop.
Every epoch:

1. Shuffle **training only**, like randomizing partitions without changing
   their records.
2. Split it into 24 mini-batches with `array_split`.
3. Forward: calculate hidden outputs and final logits.
4. Backward: calculate gradients from the loss.
5. Adam: update every weight and bias.
6. Calculate validation loss without updating the model.
7. Keep a snapshot when validation loss improves materially.
8. Stop if it stops improving for 12 consecutive epochs.
9. Restore the best snapshot before final reporting.

The validation examples are outside the optimization loop. They are analogous
to a holdout reconciliation job: it observes correctness but must not feed
records back into the load logic.

### Worked forward update

For a simplified parameter:

- current weight = `0.70`
- gradient = `0.20`
- plain learning rate = `0.05`

A plain gradient descent update is:

`new weight = 0.70 - 0.05(0.20) = 0.69`

The gradient direction increases loss, so moving opposite it reduces loss.
The example uses Adam rather than one fixed raw gradient step. Adam tracks
running gradient mean (first moment) and squared gradient (second moment),
then bias-corrects them. This usually handles different parameter scales well,
but still requires a sensible learning rate.

## 7. Loss, gradients, and regularization

For binary classification, the logistic loss for one row is:

```text
loss = -[y * log(p) + (1 - y) * log(1 - p)]
```

Tiny examples:

- True label `1`, probability `0.9`: loss is `-log(0.9) ≈ 0.105`.
- True label `1`, probability `0.2`: loss is `-log(0.2) ≈ 1.609`.
- True label `0`, probability `0.2`: loss is `-log(0.8) ≈ 0.223`.

The model is penalized much more for confident wrong predictions. A score of
0.5 has no business decision attached until a threshold is chosen.

The code uses numerically stable `np.logaddexp(0, logits) - target * logits`.
This avoids explicitly calculating unstable exponentials and logarithms.

The L2 penalty is `l2 * sum(weight^2)`. It discourages large weights. It is
not applied to biases in this implementation. **Regularization** is a set of
techniques to improve generalization:

- L2 weight penalty;
- L1 sparsity penalty;
- dropout, which masks units during training and is disabled in evaluation;
- data augmentation using valid input transformations;
- early stopping;
- smaller architecture or more representative clean data.

### Interpreting loss curves

- Train and validation loss both falling: learning useful signal.
- Train falling while validation rises: memorizing or overfitting train.
- Both high and flat: check data, shapes, learning rate, labels, and optimizer.
- Wildly changing or `NaN`: inspect scale, learning rate, overflow, and gradient
  values.
- Validation improves in tiny increments: inspect the improvement tolerance and
  stochastic seed variation.

## 8. Backpropagation in plain language

The model caches each forward activation and preactivation because gradients
depend on them. Backpropagation begins with the final loss derivative
`(sigmoid(logit) - y) / batch_size`. It then passes sensitivity backward through
each matrix:

1. Multiply the current delta by the previous activation to form weight
   gradients.
2. Sum the delta for bias gradients.
3. Move delta through the weight matrix to the previous layer.
4. Apply the ReLU derivative: pass through only where the earlier z was above
   zero.

For a simple ReLU output:

- z = -2: ReLU output 0 and derivative 0; that route contributes no gradient.
- z = 3: ReLU output 3 and derivative 1; gradient passes through.

A "dead ReLU" always produces zero for a problematic set of inputs. It is one
reason to inspect activation distributions and input scale.

## 9. Early stopping is a deployment checkpoint

The initial best validation loss is infinity and the best snapshot is the
random initial state. After each epoch, a lower validation loss replaces the
checkpoint. After 12 non-improving epochs, the loop stops. At the end it
restores the saved best weights, not the last values.

This resembles retaining the last known good generated artifact rather than
promoting the final batch solely because it ran latest.

The example's `1e-4` improvement tolerance avoids saving tiny random
fluctuations. Patience and tolerance are hyperparameters chosen by development
practice; they are not learned from a gradient.

Important modes:

- In a framework, `model.train()` enables dropout and uses training behavior
  for batch normalization.
- `model.eval()` disables those stochastic/training behaviors.
- `torch.no_grad()` or equivalent avoids building unnecessary gradient state
  during evaluation.

This NumPy MLP has no dropout or batch normalization, so the example states
that inference-mode idea conceptually rather than toggling a nonexistent flag.

## 10. Metrics walkthrough

The MLP reports binary metrics at a fixed 0.5 threshold. Suppose a 360-row
test set gives:

- TP 170, FP 30, TN 130, FN 30.

Then:

- accuracy = `(170 + 130) / 360 = 83.3%`
- precision = `170 / 200 = 85%`
- recall = `170 / 200 = 85%`
- F1 = 85%
- confusion matrix total = 360

Loss complements the thresholded metrics. Two models may both be 83% accurate,
while one is confidently wrong on the failures. Loss usually exposes those
probability differences, but the business threshold should be tuned with
validation just as in the churn example.

Report train, validation, and test separately:

- train checks learnability and indicates overfitting;
- validation supports selection;
- test estimates performance once final weights and policy are fixed.

Do not choose a "best" epoch from test loss. That reuses the test for model
selection.

## 11. Read the implementation progressively

Follow the code in this order:

1. `sigmoid` and `make_data`.
2. `split` and the 60/20/20 row counts.
3. `MLP.__init__`: architecture, weight initialization, and Adam state.
4. `forward`: the path from shape `(batch, 6)` to `(batch, 1)`.
5. `loss`: task error plus regularization.
6. `backward`: reverse gradient calculation.
7. `adam_step`: parameter update.
8. `train_batch`: one orchestration cycle.
9. `metrics`: threshold and confusion matrix.
10. `main`: preprocessing, epochs, checkpoint restore, final reporting.

Initialization matters. A normal random start scaled by `sqrt(2 / fan_in)`
is a ReLU-friendly common practice. All-zero hidden weights would make all
hidden units within a layer identical and prevent them learning different
patterns.

The exact Adam moment arrays must align with `parameters()` order:
`weight1, bias1, weight2, bias2, weight3, bias3`. Misaligned gradient state is a
subtle bug that can appear to train but produce invalid updates.

## 12. Debugging checklist

When a network fails, diagnose in increasing scope:

1. **One-row shape trace:** print/assert shapes after every layer.
2. **Finite data:** inspect `NaN`, infinity, ranges, and standardization
   denominators.
3. **Label contract:** Are labels 0/1, and does `1` mean the positive event?
4. **Tiny overfit test:** Use 5–20 examples repeatedly. A suitable small model
   should nearly memorize them before evaluating generalization.
5. **One batch:** Confirm train loss falls for one repeated batch.
6. **Gradient checks:** At least finite, nonzero, and expected scale. Numerical
   finite differences can verify selected manual gradients.
7. **Optimization:** Test a lower learning rate or plain SGD when Adam masks an
   implementation issue.
8. **Validation separation:** Check IDs, time, preprocessing statistics, and
   accidental use of validation in weight updates.
9. **Checkpoint:** Confirm that restored epoch and weights match the best
   validation result.
10. **Threshold:** Reconcile probabilities, hard decisions, and the confusion
    matrix.
11. **Seed repeat:** Repeat across multiple seeds before trusting small metric
    differences.
12. **Parity with simple model:** If a neural model loses to a logistic or tree
    baseline, inspect features, scale, and task fit before increasing depth.

Common errors:

- Broadcasting labels `(batch,)` against outputs `(batch, 1)` silently.
- Reversing label orientation.
- Accumulating gradients rather than replacing them in a framework loop.
- Optimizing through validation or forgetting to call `zero_grad()`.
- Evaluating with dropout still enabled.
- Standardizing from the whole dataset.
- Saving random last weights instead of the best checkpoint.
- Comparing loss computed with different reduction or regularization choices.
- Training on class data but inference on different units or schema.

## 13. Common architectures, without memorizing acronyms

### Dense/fully connected (MLP)

Every unit sees every input unit from the preceding layer. It is a natural
baseline for fixed-length numeric records but scales poorly for huge images or
does not directly represent order.

### Convolutional neural network (CNN)

A learned small kernel is applied across positions, so the same local feature
detector is reused across an image. It is useful where neighborhood or
locality matters. Kernel, padding, and stride determine output shape.

### Recurrent network (RNN/LSTM/GRU)

These preserve a hidden state across an ordered sequence. LSTM and GRU use
gates to better retain or forget information. They are useful for sequences but
can be harder to parallelize.

### Transformer

Self-attention lets sequence tokens form weighted mixtures of context. It uses
queries, keys, and values plus multi-head attention, feed-forward layers,
residual connections, and normalization. Attention can learn broad
dependencies but standard attention memory/time grows quickly with sequence
length. Tokenization and embedding are part of the model contract.

No architecture should be selected merely because it is advanced. Select it
because the input structure and error patterns justify it.

## 14. Framework loop mapping

The NumPy example corresponds to a typical PyTorch-style cycle:

```text
clear gradients
model outputs = model(batch)
loss = criterion(outputs, labels)
loss.backward()
optimizer.step()
```

At validation:

```text
model.eval()
no-gradient context
outputs = model(batch)
aggregate per-example loss, never average batch means without weights
restore training/best checkpoint as appropriate
```

In format-neutral terms, a complete framework package needs code/config,
architecture, parameters, preprocessing, input and output schema, class mapping,
threshold, and data/model versions.

## 15. Realistic industry decisions

### Scenario A: nightly fraud queue

A deep model improves AUC by 0.01 but consumes 4x CPU and misses the AutoSys
deadline by 20 minutes. It is not automatically the winner. Compare benefit at
the operational threshold and queue capacity against resource cost, SLA,
maintainability, and the simpler model. AUC alone does not express capacity or
latency.

### Scenario B: log/event classifier

The validation set randomly splits each machine's adjacent events. Later
timings appear in train and earlier timings in validation, creating an
unrealistic forecast. Re-split chronologically and by entity; tune on the most
recent past window, leaving a later test window untouched.

### Scenario C: recommendation exposure

Training labels reflect what previous recommendation policy showed. Missing
outcomes are not random negatives; unseen items may be good but never surfaced.
This feedback loop must be addressed in collection and experiment design, not
only by more hidden layers.

### Scenario D: batch sizing mismatch

The model passed with 128-row training batches but inference sends one row.
Verify normalization is based on saved training statistics, not current-batch
statistics, and test batch size 1, partial batch, and malformed/out-of-range
input.

### Scenario E: promising validation, failed launch

Validation loss was excellent, but production accuracy collapsed after a field
unit changed from bytes to kilobytes. Add contracts for units and ranges plus
feature-distribution monitoring. Alert and use rollback/fallback before blindly
retraining on the corrupted stream.

## 16. Serving and monitoring

A trained artifact is not a complete service. Package:

- model architecture and weights;
- training mean/scale or an equivalent preprocessing artifact;
- accepted feature names, order, dtype, units, and missing behavior;
- output class interpretation and threshold;
- framework/code/dependency versions;
- known performance, slices, limitations, and owner.

Before promotion:

- validate malformed and out-of-range inputs;
- benchmark one-row and batch throughput, p50/p99 latency, memory, and
  cold-start behavior;
- compare optimized/quantized and original numerical outputs;
- shadow-run and canary on a small workload;
- define a rollback artifact and safe fallback.

After release, monitor input distributions, score distributions, prediction
rate, latency, errors, resource use, and delayed ground-truth metrics. Scheduler
or Kubernetes health proves process availability, not model quality.

## 17. Ethics and safe use

Deep models can be less interpretable and can memorize sensitive information.
Document lawful purpose, prohibited use, privacy, retention, access control,
human oversight, appeal, and security. Evaluate error burden on relevant
groups where appropriate and report small-slice uncertainty. Avoid inferring
protected attributes merely to improve a workflow.

For a consequential action, raw probability is not enough: users need
explanations of practical factors, thresholds, uncertainty, and a controlled
override. The simplest acceptable model is often easier to audit and safer to
operate.

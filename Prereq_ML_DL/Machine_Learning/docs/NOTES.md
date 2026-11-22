# Machine Learning for a Data-Pipeline Developer

## 1. Start with the business decision

Machine learning (ML) is a way to make a rule from examples rather than hand-code
that rule. In ETL terms, ordinary code says, "if tenure is below 10, flag the
customer"; ML uses historical rows to estimate which combinations of values
are associated with an outcome.

First define:

- **Prediction unit (grain):** the entity receiving a prediction, analogous to
  the grain of a fact table. Here it is one customer snapshot, not every ticket
  row.
- **Decision time:** when the score is needed. Features may only use facts
  available at that time.
- **Outcome/label/target:** the future fact being predicted. For churn, `1`
  means the customer cancels during the agreed observation window; `0` means
  they do not.
- **Action:** what a user or downstream job does with the score. Examples are a
  retention call, manual review, inventory order, or no action.
- **Success and cost:** what false alarms and missed events cost.

The first line of a model design should read like:

> At the start of each month, score active customer accounts using data known
> at that point, then predict cancellation within the next 60 days so the
> retention team can contact the highest-value, highest-risk subset.

Without a decision, a model with excellent metrics may be useless. A score that
arrives after the retention team extracts its daily work queue is like a batch
landing after its downstream job's trigger.

### Useful vocabulary

- **Feature:** an input column, such as tenure or monthly charge.
- **Example:** one row used to learn or evaluate.
- **Model:** the fitted mathematical rule.
- **Training:** estimating model parameters from examples.
- **Prediction/score:** the model's output for a new row.
- **Inference:** running a trained model on new data; it does not update the
  model.
- **Supervised learning:** learning from input rows and known labels.
- **Classification:** predicting a category, such as churn/no churn.
- **Regression:** predicting a quantity, such as call volume next week.
- **Unsupervised learning:** finding structure without labels, such as clusters.

## 2. Think in stages, like an orchestrated pipeline

A small ML workflow closely resembles a controlled warehouse batch:

```text
source data -> snapshot -> split -> fit transforms -> train models
                         -> validate model/settings -> seal test estimate
                         -> package -> deploy -> score -> monitor outcomes
```

The analogy is not exact:

- A database transform implements rules we supplied.
- A training step *discovers parameters* by repeatedly reducing prediction
  error.
- A successful load does not prove a model is useful; evaluation compares
  predictions with withheld outcomes.
- A model and preprocessing are one deployable pipeline. Deploying weights
  without the fitted imputation, encoders, column order, and scaling is like
  running an Informatica mapping with the wrong lookup file.

### Train, validation, and test: the controlled walkthrough

Suppose there are 10 customer records with outcomes:

| Row set | Count | Allowed use |
|---|---:|---|
| Train | 6 | Fit transforms and learn parameters |
| Validation | 2 | Compare models, settings, and thresholds |
| Test | 2 | Estimate final performance once |

If validation records are used to choose a model and then are reported as final
proof, the result is optimistic. That is similar to tuning a data-quality rule
against a sample and claiming the same sample independently certified it.

Keep the test set sealed until the model, preprocessing, and decision threshold
are fixed. Repeatedly changing the system after seeing test results makes the
test data another validation set.

The example creates 2,400 deterministic customer snapshots:

- 60% train = 1,440 rows
- 20% validation = 480 rows
- 20% test = 480 rows

`group_split` shuffles rows deterministically and separates the selected row
indices. Because this synthetic dataset has one row per customer, its
customer-level split is also the row split. With multiple monthly observations
per customer, split by customer (and usually by time), not by arbitrary rows.
Otherwise the same customer's January and February details could be split
across train and test, letting the model memorize identity-like patterns.

## 3. Prevent leakage before measuring anything

**Leakage** is using information that is not legitimately available at decision
time. It is the ML equivalent of a target mapping joining a field populated by a
later process and still expecting a correct pre-process result.

Common leakage cases:

- Joining a field such as `refund_after_cancellation`.
- Aggregate values containing future activity.
- A model input derived from the target.
- Fitting a scaler on train plus validation plus test.
- Letting a customer identifier encode a history that will not generalize.

The example deliberately creates `refund_after_cancellation`:

```python
"refund_after_cancellation": np.where(
    label, rng.normal(80, 8, n), rng.normal(3, 2, n)
)
```

Average values differ dramatically by outcome, so using this field could
produce unrealistic performance. `Preprocessor.numeric` omits it. The printed
warning is documentation, not protection; production teams should also add
schema allowlists, lineage, and timestamp tests.

**Training-serving skew** occurs when training and live inference produce
different features. Audit source tables, units, null behavior, category
vocabulary, version, and column order as one contract.

### Tiny leakage example

Ten customers include `refund_after_cancellation`; eight refunds above $50
correspond to churn. Predicting churn using the refund looks perfect, but the
refund exists only after cancellation. At decision time the true value is
unknown, so that apparent accuracy cannot be deployed.

## 4. Preprocessing is a fitted production transform

The example's `Preprocessor.fit` estimates transformations from training rows
only, while `transform` applies the saved values to every partition.

For each numeric column:

1. Compute the training median.
2. Replace missing or non-finite values with that median.
3. Compute the filled training mean and standard deviation.
4. Standardize each value:

   `z = (value - training_mean) / training_standard_deviation`

### Worked standardization

Training charges are `[40, 60, 80]`:

- mean = 60
- standard deviation (population version used by NumPy) = about 16.33
- a $76.33 customer becomes `(76.33 - 60) / 16.33 = 1`

Standardization does not add business information; it puts columns on
comparable scales and can make optimization more stable. The same training
mean and scale must be saved for validation, test, and production.

Fitting validation medians is wrong: the validation batch would influence its
own transformation. Fitting the live request's median is also wrong and may be
impossible for a single record.

Categorical encoding requires a fixed vocabulary. The example maps:

```text
month  -> [1, 0]
annual -> [0, 1]
```

This is **one-hot encoding**, first-use meaning: represent one category with
binary indicator columns. A production pipeline must decide how to encode
unknown values such as a new contract type. The example is intentionally fixed
to the two generated categories.

## 5. Baselines and models in this example

Always establish a simple baseline. A model that cannot beat "predict no one
churns" or "use the historical churn rate" has not demonstrated value, even if
its headline accuracy is high.

### Logistic regression

**Logistic regression** estimates a weighted score:

`score = weight_1 * feature_1 + ... + bias`

It passes that score through a sigmoid:

`probability = 1 / (1 + exp(-score))`

The sigmoid converts any real score to a value from 0 to 1. With weights 0.5
for standardized charges and -0.4 for standardized tenure, and bias -1:

- charges z-score = 1
- tenure z-score = 2
- score = `0.5(1) - 0.4(2) - 1 = -1.3`
- probability = about `0.214`

This is not a guarantee that 21.4% of identical customers churn. It is the
model's estimated probability, whose quality depends on data and calibration.

The class is trained with gradient descent: it calculates prediction errors,
calculates the direction that reduces average error, then makes a small update.
`learning_rate` controls update size; `epochs` controls full passes over train
data; L2 regularization penalizes large weights to reduce instability and
overfitting.

### Decision trees and the random forest

A **decision tree** asks sequential `<=` / `>` questions. At each node it chooses
the feature and threshold that best separate outcomes on training data. For
example: "Is tenure <= 8 months?" Each leaf stores the training churn rate.

The local tree implementation:

- limits depth, so paths cannot grow indefinitely;
- requires a minimum leaf size;
- compares candidate splits by impurity reduction.

A **random forest** trains many decorrelated trees on bootstrap samples
(training rows sampled with replacement) and averages their predictions. It is
an ensemble: several imperfect models can be less noisy than one model. It
often works well on tabular data but is not automatically fair, causal, or
leakage-proof.

## 6. Classification metrics and interpretation

A probability alone does not decide whom to call. A **threshold** turns scores
into actions:

```text
if probability >= threshold: predict positive (churn)
else: predict negative (stay)
```

Consider 100 validation customers:

- 20 actually churned and 80 stayed.
- At threshold 0.5, 15 churners and 10 stayers are selected.

The **confusion matrix** is:

```text
                     predicted churn  predicted stay
actually churn              15             5
actually stay               10            70
```

Terminology and formulas:

- **True positives (TP):** 15 correctly selected churners.
- **False positives (FP):** 10 stayers incorrectly selected.
- **True negatives (TN):** 70 correctly unselected stayers.
- **False negatives (FN):** 5 churners missed.
- **Precision = TP / (TP + FP):** `15/25 = 60%`; of selected rows, 60% are
  actually churners. This matters when calls have limited capacity.
- **Recall = TP / (TP + FN):** `15/20 = 75%`; 75% of actual churners are
  found. This matters when misses are expensive.
- **Specificity = TN / (TN + FP):** `70/80 = 87.5%`; 87.5% of stayers are
  correctly left alone.
- **Accuracy = (TP + TN) / all:** `85%`. It can hide poor minority
  performance.
- **F1:** the harmonic mean of precision and recall. Here it is about 66.7%.
  It is useful when precision and recall both matter, but not a substitute for
  costs.
- **Balanced accuracy:** `(recall + specificity) / 2 = 81.25%`, giving each
  class equal weight.
- **Selection rate:** predicted-positive share, here 25%.

### Threshold as an operations decision

The example searches thresholds only on validation. It chooses the highest
recall while retaining at least 55% precision, a proxy for contact capacity and
quality. Lowering the threshold usually selects more people: recall rises, but
precision often falls because more stayers enter the queue.

Imagine a call team can handle only 200 customers/week, and each useless call
costs $8 while preventing one churn is worth $120. A 60%-precision queue of 200
contains 120 expected churners, but costs and value should be calculated using
the actual threshold and outcome base rate. Use expected capacity, cost, and
benefit—not only F1—to approve a setting.

## 7. Cross-validation and hyperparameters

A **hyperparameter** controls training but is not learned in the gradient or
tree update. Examples include learning rate, number of trees, tree depth, and
regularization strength.

With one split, a performance difference might be sample noise. **K-fold
cross-validation** rotates K validation sections within training:

```text
fold 1: [validate A] train B, C, D, E
fold 2: [validate B] train A, C, D, E
...
```

Each fold fits preprocessing and the model anew to avoid leakage. Grouped folds
keep all rows for an entity together; time-series folds keep earlier data in
train and later data in validation.

Cross-validation is for development. A final sealed test remains useful for a
single, unbiased estimate after settings are selected.

## 8. Execute the churn example mentally and then run it

`examples/churn_pipeline.py` follows this sequence:

1. `make_customers` creates correlated source features and a binary outcome.
2. `group_split` creates deterministic 60/20/20 indices.
3. `Preprocessor.fit(data, train)` learns medians, mean, scale, and categories.
4. The same transform object processes train, validation, and test.
5. Logistic regression and a 35-tree forest fit only training rows.
6. Each model gets a threshold selected with validation data.
7. The model with highest validation balanced accuracy wins.
8. The chosen test score is printed, with the winning validation threshold.
9. Region slices are an audit, not a model-selection step. Region was
   excluded from inputs.

Typical expected output is deterministic metric dictionaries. Exact values can
change if the formulas, NumPy version, or random process changes, so store
expected bounds or end-to-end behavior rather than hard-coding every decimal in
production tests.

### Why region appears in output

`region` is excluded from model features but retained for a post-hoc performance
audit. Averages can conceal unequal errors: overall recall may be good while
region 2 has very poor recall. If a slice is too small, report its size and use
uncertainty intervals before concluding that a difference is real.

## 9. Debugging checklist

Use this order instead of immediately adding model complexity:

1. **Reconcile grain:** Are there exactly one label and snapshot per scored
   entity/time? Check duplicate keys.
2. **Validate target:** Are positive and negative definitions stable? Is the
   outcome window complete?
3. **Check time:** Was every feature known before decision time?
4. **Inspect split:** Do customer IDs, timestamps, or correlated batches cross
   partitions unexpectedly?
5. **Inspect schema:** Compare dtypes, ranges, missingness, allowed categories,
   and row counts by split.
6. **Verify preprocessing:** Fit only on training; save and reuse all state.
7. **Run a tiny deterministic case:** Can logistic regression overfit 10 clear
   records? If not, investigate shapes or updates.
8. **Check prediction range:** Probabilities must be finite and in `[0, 1]`.
9. **Check class baseline:** Print class prevalence and all-positive/
   all-negative behavior.
10. **Check threshold and metrics:** Confirm the confusion matrix reconciles to
    row count: `TP + FP + TN + FN = N`.
11. **Check selected artifact:** Did the final report use the saved winner and
    threshold?
12. **Run slices and scenarios:** Test regions, time windows, high-value
    customers, and missing/unknown inputs.

Common errors:

- Shape mismatch from inconsistent column order: solve by named schema and
  tests, not by guessing dimensions.
- `NaN` loss: look for missing inputs, division by zero, or invalid logs.
- Perfect validation: check leakage and duplicated entities first.
- Worse-than-baseline behavior: verify label orientation (`1` means what?),
  preprocessing order, and split distribution.
- Great train metrics, poor validation: likely overfitting; increase clean data,
  simplify model, regularize, or improve generalizable features.
- Great metrics, weak value: estimate capacity, latency, cost, and action.

## 10. Realistic industry decisions

### Scenario A: retention queue

A churn model catches 80% of churners but selects 40% of all customers, while
the team can call only 8%. The team should not reject the
model solely on recall. Construct a queue at the actual contact capacity,
inspect precision and expected saves at the capacity cutoff, and compare
against simple tenure/usage rules. Consider a value-aware ranking.

### Scenario B: credit or sensitive service

A model raises overall accuracy but has materially different false-negative
rates across relevant lawful audit groups. Aggregate accuracy is not approval.
Document intended use, test data slices, human review, appeals, privacy, and
legal constraints. Do not infer protected traits for convenience.

### Scenario C: seasonal drift

Churn rises every December. Is input drift bad if the outcome rate changed with
normal seasonality? Compare recent feature distributions, calibration, and
outcome relationships with historical equivalent windows. Add month/time
features only if known at scoring time and supported by enough history.

### Scenario D: new product category

Live data contains contract type `lifetime`, absent in training. Silently
dropping it or mapping it arbitrarily breaks the inference contract. Define an
unknown-category path, alert on rate, and retrain under a controlled process.
Do not refit preprocessing on a single production batch.

## 11. Deployment and operations

Treat a model release like an auditable batch release:

- Register source snapshot, code revision, dependency versions, random seed,
  schema, feature logic, preprocessing artifact, weights, metrics, threshold,
  and model card.
- Shadow-score without action before a canary release.
- Monitor row counts, freshness, missingness, category unknowns, score
  distributions, latency, and errors.
- Once labels arrive, monitor outcome rate, precision/recall, calibration, and
  slices. Delayed outcomes mean lag-aware dashboards are essential.
- Define retraining triggers and rollback/fallback behavior. "Drift detected"
  is not actionable without an owner, threshold, and response.

**Data drift** means input distributions changed. **Concept drift** means the
relationship from inputs to labels changed. They may occur separately and
require different responses. Monitoring a scheduler success code proves the job
ran; it does not prove predictions remain useful.

## 12. Responsible interpretation

Feature importance is not causality. If monthly charge is associated with
churn, lowering charge is not guaranteed to prevent churn; hidden variables may
explain both.

A model can be statistically accurate and operationally unsuitable if it is too
late, too opaque, expensive to maintain, privacy-invasive, or unfair in its
error burden. Include intended and prohibited uses, human appeal, data
retention, access control, and recourse in the model card.

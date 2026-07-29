# CardioTrust Model Card

Status date: 2026-07-28  
Version: 2.0, local research prototype

## Intended use

CardioTrust predicts the binary `cardio` label in the host-provided tabular
dataset. It is a competition prototype for research and demonstration only.
It is not a diagnosis, individual risk estimate, medical device, or triage
system.

## Data

- Source rows: 70,000
- Modeling rows: 69,918
- Excluded before splitting: all 82 records belonging to 41 duplicated
  predictor-profile groups
- Conflicting labels among duplicated profiles: 17 groups
- Missing-value encoding in source: none
- Implausible blood-pressure records: 1,334

The upstream Kaggle metadata displays the dataset license as `Unknown`.
Row-level data are not included in the publishable project surface.

## Model and decision policy

The selected estimator is sigmoid-calibrated histogram gradient boosting.
Selection used the lowest Brier score from 3 repeats of 5-fold development
out-of-fold predictions. Calibration used three inner folds. Binary decisions
use a fixed threshold of 0.5.

The demo withholds a label when:

- age, height, weight, or blood-pressure values fail fixed plausibility checks
- confidence is below `0.6058905448`, learned from development predictions to
  target 80% coverage

## Locked validation

The protocol and code hashes were frozen before the final holdout was observed.
The target-stratified 20% holdout uses seed `20260801` and contains 13,984
records.

| Metric | Estimate | 95% bootstrap interval |
|---|---:|---:|
| ROC AUC | 0.8014 | 0.7942-0.8087 |
| Average precision | 0.7865 | 0.7765-0.7960 |
| Balanced accuracy | 0.7349 | 0.7279-0.7429 |
| Sensitivity | 0.7029 | 0.6922-0.7130 |
| Specificity | 0.7669 | 0.7573-0.7773 |
| Brier score | 0.1806 | 0.1771-0.1841 |
| Log loss | 0.5412 | 0.5330-0.5496 |

ECE with 10 equal-width bins is 0.0026. Its naive percentile-bootstrap
interval is not reported because the resampled ECE statistic is upward-biased
and the resulting interval does not contain the point estimate.

At the development-learned 80% policy, holdout coverage is 80.6% and error is
22.07% (Wilson 95% interval 21.32%-22.85%). These are empirical results, not a
formal risk guarantee.

## Subgroup limitations

The weakest reported group is `age_60_plus`: ROC AUC 0.7102, balanced accuracy
0.6068, and only 65.0% coverage under the fixed selective policy. The model has
no external, temporal, geographic, hospital, or prospective validation.
Source gender values are opaque two-category codes and do not represent the
full range of sex or gender.

## Reproducibility

The locked code hashes are in `docs/VALIDATION_LOCK.md`. Two full runs produced
byte-identical metrics, selective-policy, subgroup, fold, and interval
artifacts. Exact environment versions and data hashes are recorded under
`artifacts/`.

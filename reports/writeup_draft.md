# CardioTrust: a cardiovascular model that knows when not to answer

**Status:** local draft, not submitted  
**Track:** select in Kaggle before submission  
**Competition:** Byte2Beat

## Executive summary

CardioTrust is a research prototype for predicting the binary label in a
70,000-row cardiovascular dataset. Its central design choice is selective
prediction: when confidence is low or an input is implausible, the system
withholds a label rather than forcing a binary answer.

The selected calibrated gradient-boosting model achieved 0.8014 ROC AUC
(95% CI 0.7942-0.8087), 0.7865 average precision, and a 0.1806 Brier score on
a protocol-locked 13,984-row holdout. At approximately 80% coverage, empirical
holdout error declined from 26.51% to 22.07%. Performance was materially weaker
in the source age-60-plus subgroup, so the project does not claim clinical
readiness.

## Why abstention matters

Most demonstration classifiers return an answer for every record, including
profiles unlike reliable training examples and measurements that are clearly
invalid. CardioTrust instead exposes three states:

1. a model signal when confidence exceeds the development-learned threshold
2. escalation when the profile lies in the uncertainty region
3. an input-quality stop when measurements fail fixed plausibility rules

The result is still only a prediction of the source dataset label. Abstention
does not transform it into a diagnostic tool.

## Data quality

The host-provided primary table contains 70,000 rows, no encoded missing
values, and a nearly balanced target. It contains 41 duplicated predictor
profiles spanning 82 records; 17 groups have conflicting targets. All 82
records are excluded before splitting rather than selecting one target or
allowing identical profiles across validation boundaries. The table also
contains implausible values:

- 53 heights outside 120-220 cm
- 7 weights outside 30-250 kg
- 1,334 rows with invalid or reversed blood pressure

Invalid measurements are replaced with missing values before modeling, and
explicit invalidity indicators are retained. Imputation medians are learned
inside each training fold.

## Validation design

Before observing the final result, the code hashes and protocol were frozen.
The modeling data is split into 80% development and 20% holdout using
deadline-derived seed `20260801` and target stratification. Model comparison
uses 3 repeats of 5 shuffled development folds. Each outer training fit
contains three-fold sigmoid calibration. Selection is based on development
Brier score; the locked holdout is evaluated once.

| Development model | ROC AUC | AP | Brier | ECE |
|---|---:|---:|---:|---:|
| Calibrated logistic regression | 0.7919 | 0.7725 | 0.1868 | 0.0339 |
| Calibrated histogram gradient boosting | 0.8028 | 0.7861 | 0.1798 | 0.0052 |

## Holdout results

| Metric | Value |
|---|---:|
| ROC AUC | 0.8014 |
| Average precision | 0.7865 |
| Balanced accuracy | 0.7349 |
| Sensitivity | 0.7029 |
| Specificity | 0.7669 |
| Brier score | 0.1806 |
| Log loss | 0.5412 |
| ECE, 10 bins | 0.0026 |

The naive percentile-bootstrap interval for ECE is not reported because ECE
is upward-biased under resampling here and the resulting bounds do not contain
the point estimate. The point value is exploratory; the other metrics retain
their stratified-bootstrap intervals.

Confidence thresholds are derived only from development out-of-fold
probabilities and applied unchanged to the holdout.

| Target coverage | Observed coverage | Error rate | Balanced accuracy |
|---:|---:|---:|---:|
| 100% | 100.0% | 0.2651 | 0.7349 |
| 90% | 90.8% | 0.2450 | 0.7549 |
| 80% | 80.6% | 0.2207 | 0.7794 |
| 70% | 70.7% | 0.1990 | 0.8014 |
| 60% | 60.2% | 0.1792 | 0.8204 |

These results describe selected holdout subsets. They do not establish a
formal error guarantee or clinical safety.

## Interpretability and subgroup evidence

Permutation importance identifies systolic blood pressure, age, and
cholesterol category as the strongest global contributors. The demo also
performs per-profile sensitivity analysis by replacing one entered value at a
time with its development-set reference value. This measures model
sensitivity, not causality.

The source age-60-plus subgroup had 0.7102 ROC AUC and 0.6068 balanced
accuracy, substantially below the younger groups. Its selective coverage was
only 65.0% under the single global threshold, versus 90.5% below age 50. This
limitation is shown prominently rather than hidden behind the overall score.

## Reproducibility

The project pins Python packages, records data SHA-256 hashes and environment
versions, uses fixed seeds, and emits machine-readable metrics. A second full
run produced byte-identical metric, selective-prediction, subgroup, fold, and
interval files. The Dev Container defines a Coder app, autostart command, and
health check for the Streamlit service on port 8501; a live Coder recording is
still required.

## Limitations and responsible use

- The upstream dataset license is displayed as `Unknown`; no row-level data is
  redistributed.
- Collection setting, sites, dates, consent, and label construction are not
  documented by the host.
- There is no external, temporal, geographic, hospital, or prospective
  validation.
- The two source gender codes are incomplete and should not be generalized.
- Confidence is model confidence, not patient-specific medical certainty.
- CardioTrust must not be used for diagnosis, treatment, triage, or emergency
  decisions.

## Submission blockers

Before publication, the team must resolve dataset/model licensing, obtain the
organizer's Coder integration instructions, demonstrate that integration in
the demo, create a public Kaggle notebook and public demo, select a track, and
receive explicit approval for the one final submission.

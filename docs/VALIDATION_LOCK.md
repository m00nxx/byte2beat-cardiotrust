# CardioTrust Final Validation Lock

Lock date: 2026-07-28  
Status: frozen before observing the `20260801` holdout

## Locked protocol

- Primary data: host-provided `cardio_base.csv`
- Exclude every row whose full predictor profile occurs more than once
- Fixed plausibility rules; fold-local median imputation
- Development seed: `42`
- Final holdout seed: `20260801`, derived from the competition deadline
- Holdout fraction: 20%, target-stratified
- Development validation: 3 repeats x 5 folds
- Inner probability calibration: 3-fold sigmoid calibration
- Candidate models: logistic regression and histogram gradient boosting
- Selection metric: development repeated-OOF Brier score
- Classification threshold: fixed at `0.5`
- Selective policy: development confidence quantile targeting 80% coverage
- Uncertainty: 500 stratified holdout bootstrap iterations
- No hyperparameter or policy changes after the first `20260801` evaluation

## Locked code hashes

| File | SHA-256 |
|---|---|
| `src/run_experiment.py` | `30ACF45EB3BECD80EEC8DD1853514F5C5ACBEA9A8986D8037387658F175A486F` |
| `src/evaluation.py` | `4FDBF6969A3D3711059673B0E659848D15349FE06CDD5D192CA5C85A256BEBD5` |
| `src/features.py` | `10417D49019CEE328033C2A8D93CE0F848B9EB4EAAF32355E9B0B855C96CA1F8` |
| `src/inference.py` | `A04B0F1E08DD5B9A4E95956F32EBF8D0436E82FFAF68C22F5280BAA4085FA3B5` |
| `requirements.txt` | `34574F4274FF48F96649FA9554A55FAD510A87E4C638737199ED4E44D5AF659E` |

Documentation, demo presentation, and tests may be improved after this lock.
Any modification to the locked training or evaluation files invalidates the
claim that the final holdout was observed only after protocol freeze.

from __future__ import annotations

from statistics import NormalDist

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.base import clone
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from threadpoolctl import threadpool_limits


def expected_calibration_error(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    bins: int = 10,
) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    bucket = np.clip(np.digitize(probabilities, edges[1:-1]), 0, bins - 1)
    error = 0.0
    for index in range(bins):
        selected = bucket == index
        if not selected.any():
            continue
        error += selected.mean() * abs(
            y_true[selected].mean() - probabilities[selected].mean()
        )
    return float(error)


def classification_metrics(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    predictions = (probabilities >= threshold).astype(int)
    positive = y_true == 1
    negative = ~positive
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "average_precision": float(average_precision_score(y_true, probabilities)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, predictions)),
        "sensitivity": float((predictions[positive] == 1).mean()),
        "specificity": float((predictions[negative] == 0).mean()),
        "brier": float(brier_score_loss(y_true, probabilities)),
        "log_loss": float(log_loss(y_true, probabilities)),
        "ece_10": expected_calibration_error(y_true, probabilities, bins=10),
        "threshold": float(threshold),
    }


def repeated_oof_probabilities(
    model,
    features: pd.DataFrame,
    target: np.ndarray,
    *,
    folds: int,
    repeats: int,
    seed: int,
    n_jobs: int = 1,
) -> tuple[np.ndarray, pd.DataFrame]:
    probability_sum = np.zeros(len(target), dtype=float)
    prediction_counts = np.zeros(len(target), dtype=int)
    fold_rows: list[dict] = []

    tasks = []
    for repeat in range(repeats):
        splitter = StratifiedKFold(
            n_splits=folds,
            shuffle=True,
            random_state=seed + repeat,
        )
        for fold, (train_positions, validation_positions) in enumerate(
            splitter.split(features, target),
            start=1,
        ):
            tasks.append(
                delayed(_fit_validation_fold)(
                    model,
                    features,
                    target,
                    train_positions,
                    validation_positions,
                    repeat + 1,
                    fold,
                )
            )

    with threadpool_limits(limits=1):
        completed = Parallel(
            n_jobs=n_jobs,
            backend="threading",
        )(tasks)
    for validation_positions, probabilities, fold_row in completed:
        probability_sum[validation_positions] += probabilities
        prediction_counts[validation_positions] += 1
        fold_rows.append(fold_row)

    if not np.all(prediction_counts == repeats):
        raise RuntimeError("Repeated OOF predictions do not cover every row equally")

    return probability_sum / prediction_counts, pd.DataFrame(fold_rows)


def _fit_validation_fold(
    model,
    features: pd.DataFrame,
    target: np.ndarray,
    train_positions: np.ndarray,
    validation_positions: np.ndarray,
    repeat: int,
    fold: int,
) -> tuple[np.ndarray, np.ndarray, dict]:
    fitted = clone(model)
    fitted.fit(features.iloc[train_positions], target[train_positions])
    probabilities = fitted.predict_proba(features.iloc[validation_positions])[:, 1]
    fold_row = {
        "repeat": repeat,
        "fold": fold,
        "validation_n": len(validation_positions),
        **classification_metrics(
            target[validation_positions],
            probabilities,
            threshold=0.5,
        ),
    }
    return validation_positions, probabilities, fold_row


def wilson_interval(
    events: int,
    total: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    if total <= 0:
        return float("nan"), float("nan")
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    proportion = events / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    margin = (
        z
        * np.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return float(max(0.0, centre - margin)), float(min(1.0, centre + margin))


def selective_table(
    y_reference: np.ndarray,
    probabilities_reference: np.ndarray,
    y_test: np.ndarray,
    probabilities_test: np.ndarray,
) -> pd.DataFrame:
    reference_confidence = np.maximum(
        probabilities_reference,
        1.0 - probabilities_reference,
    )
    test_confidence = np.maximum(probabilities_test, 1.0 - probabilities_test)
    reference_predictions = (probabilities_reference >= 0.5).astype(int)
    test_predictions = (probabilities_test >= 0.5).astype(int)

    rows = []
    for target_coverage in (1.0, 0.95, 0.90, 0.80, 0.70, 0.60):
        confidence_threshold = (
            0.5
            if target_coverage == 1.0
            else float(
                np.quantile(
                    reference_confidence,
                    1.0 - target_coverage,
                    method="higher",
                )
            )
        )
        reference_selected = reference_confidence >= confidence_threshold
        test_selected = test_confidence >= confidence_threshold

        reference_errors = int(
            np.sum(
                y_reference[reference_selected]
                != reference_predictions[reference_selected]
            )
        )
        test_errors = int(
            np.sum(y_test[test_selected] != test_predictions[test_selected])
        )
        reference_low, reference_high = wilson_interval(
            reference_errors,
            int(reference_selected.sum()),
        )
        test_low, test_high = wilson_interval(
            test_errors,
            int(test_selected.sum()),
        )

        rows.append(
            {
                "target_coverage": target_coverage,
                "confidence_threshold": confidence_threshold,
                "development_coverage": float(reference_selected.mean()),
                "development_selected_n": int(reference_selected.sum()),
                "development_error_rate": reference_errors
                / int(reference_selected.sum()),
                "development_error_ci_low": reference_low,
                "development_error_ci_high": reference_high,
                "observed_coverage": float(test_selected.mean()),
                "selected_n": int(test_selected.sum()),
                "error_rate": test_errors / int(test_selected.sum()),
                "error_rate_ci_low": test_low,
                "error_rate_ci_high": test_high,
                "balanced_accuracy": float(
                    balanced_accuracy_score(
                        y_test[test_selected],
                        test_predictions[test_selected],
                    )
                ),
            }
        )
    return pd.DataFrame(rows)


def subgroup_audit(
    features: pd.DataFrame,
    y_true: np.ndarray,
    probabilities: np.ndarray,
    *,
    classification_threshold: float,
    confidence_threshold: float,
) -> pd.DataFrame:
    age_band = pd.cut(
        features["age_years"],
        bins=[0, 49.999, 59.999, np.inf],
        labels=["under_50", "50_to_59", "60_plus"],
    )
    groups = {
        "gender_1": features["gender"] == 1,
        "gender_2": features["gender"] == 2,
        "age_under_50": age_band == "under_50",
        "age_50_to_59": age_band == "50_to_59",
        "age_60_plus": age_band == "60_plus",
    }

    predictions = (probabilities >= classification_threshold).astype(int)
    confidence = np.maximum(probabilities, 1.0 - probabilities)
    rows = []
    for name, mask_series in groups.items():
        mask = mask_series.to_numpy()
        group_y = y_true[mask]
        group_p = probabilities[mask]
        group_predictions = predictions[mask]
        selected = confidence[mask] >= confidence_threshold
        if mask.sum() < 100 or np.unique(group_y).size < 2:
            continue

        selected_errors = int(
            np.sum(group_y[selected] != group_predictions[selected])
        )
        rows.append(
            {
                "group": name,
                "n": int(mask.sum()),
                "prevalence": float(group_y.mean()),
                "roc_auc": float(roc_auc_score(group_y, group_p)),
                "balanced_accuracy": float(
                    balanced_accuracy_score(group_y, group_predictions)
                ),
                "brier": float(brier_score_loss(group_y, group_p)),
                "ece_10": expected_calibration_error(group_y, group_p, bins=10),
                "selective_coverage": float(selected.mean()),
                "selective_n": int(selected.sum()),
                "selective_error_rate": selected_errors / int(selected.sum()),
            }
        )
    return pd.DataFrame(rows)


def bootstrap_metric_intervals(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    *,
    threshold: float,
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    class_positions = [
        np.flatnonzero(y_true == label) for label in np.unique(y_true)
    ]
    estimates = classification_metrics(y_true, probabilities, threshold)
    sampled: dict[str, list[float]] = {
        name: []
        for name in estimates
        if name != "threshold"
    }

    for _ in range(iterations):
        positions = np.concatenate(
            [
                rng.choice(group, size=len(group), replace=True)
                for group in class_positions
            ]
        )
        values = classification_metrics(
            y_true[positions],
            probabilities[positions],
            threshold,
        )
        for name in sampled:
            sampled[name].append(values[name])

    rows = []
    for name, values in sampled.items():
        rows.append(
            {
                "metric": name,
                "estimate": estimates[name],
                "ci_low": float(np.quantile(values, 0.025)),
                "ci_high": float(np.quantile(values, 0.975)),
                "bootstrap_iterations": iterations,
            }
        )
    return pd.DataFrame(rows)


def error_profile_summary(
    features: pd.DataFrame,
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float,
) -> pd.DataFrame:
    predictions = (probabilities >= threshold).astype(int)
    outcome = np.select(
        [
            (y_true == 1) & (predictions == 1),
            (y_true == 0) & (predictions == 0),
            (y_true == 0) & (predictions == 1),
            (y_true == 1) & (predictions == 0),
        ],
        ["true_positive", "true_negative", "false_positive", "false_negative"],
        default="unknown",
    )
    frame = features[
        [
            "age_years",
            "bmi",
            "systolic_bp",
            "diastolic_bp",
            "cholesterol",
            "glucose",
        ]
    ].copy()
    frame["outcome"] = outcome
    frame["probability"] = probabilities
    frame["target"] = y_true
    return (
        frame.groupby("outcome", observed=True)
        .agg(
            n=("target", "size"),
            target_prevalence=("target", "mean"),
            mean_probability=("probability", "mean"),
            age_years_mean=("age_years", "mean"),
            bmi_mean=("bmi", "mean"),
            systolic_bp_mean=("systolic_bp", "mean"),
            diastolic_bp_mean=("diastolic_bp", "mean"),
            cholesterol_mean=("cholesterol", "mean"),
            glucose_mean=("glucose", "mean"),
        )
        .reset_index()
    )

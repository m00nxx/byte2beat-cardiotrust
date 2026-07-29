from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.evaluation import (
    bootstrap_metric_intervals,
    classification_metrics,
    error_profile_summary,
    repeated_oof_probabilities,
    selective_table,
    subgroup_audit,
)
from src.features import build_reference_profile, engineer_features


SEED = 42
HOLDOUT_SEED = 20260801
OOF_FOLDS = 5
OOF_REPEATS = 3
BOOTSTRAP_ITERATIONS = 500
OUTER_JOBS = max(1, min(4, int(os.environ.get("CARDIOTRUST_JOBS", "4"))))

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
ARTIFACT_DIR = ROOT / "artifacts"
FIGURE_DIR = ARTIFACT_DIR / "figures"
REPORT_DIR = ROOT / "reports"

TARGET = "cardio"
PRIMARY_DATA = RAW_DIR / "cardio_base.csv"
PROCESSED_DATA = RAW_DIR / "cardiac_failure_processed.csv"
HEART_DATA = RAW_DIR / "heart_processed.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_models() -> dict[str, CalibratedClassifierCV]:
    logistic = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    C=1.0,
                    max_iter=3000,
                    random_state=SEED,
                ),
            ),
        ]
    )
    gradient_boosting = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            (
                "model",
                HistGradientBoostingClassifier(
                    learning_rate=0.06,
                    max_iter=250,
                    max_leaf_nodes=15,
                    min_samples_leaf=50,
                    l2_regularization=1.0,
                    random_state=SEED,
                ),
            ),
        ]
    )
    return {
        "calibrated_logistic": CalibratedClassifierCV(
            logistic,
            method="sigmoid",
            cv=3,
            n_jobs=1,
        ),
        "calibrated_hist_gradient_boosting": CalibratedClassifierCV(
            gradient_boosting,
            method="sigmoid",
            cv=3,
            n_jobs=1,
        ),
    }


def save_roc_pr_plot(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    destination: Path,
) -> None:
    false_positive_rate, true_positive_rate, _ = roc_curve(y_true, probabilities)
    precision, recall, _ = precision_recall_curve(y_true, probabilities)

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].plot(false_positive_rate, true_positive_rate, color="#D1495B", lw=2)
    axes[0].plot([0, 1], [0, 1], color="#6C757D", ls="--")
    axes[0].set(
        xlabel="False-positive rate",
        ylabel="True-positive rate",
        title="ROC",
    )
    axes[1].plot(recall, precision, color="#00798C", lw=2)
    axes[1].axhline(y_true.mean(), color="#6C757D", ls="--")
    axes[1].set(
        xlabel="Recall",
        ylabel="Precision",
        title="Precision-recall",
    )
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def save_calibration_plot(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    destination: Path,
) -> None:
    observed, predicted = calibration_curve(
        y_true,
        probabilities,
        n_bins=10,
        strategy="quantile",
    )
    figure, axis = plt.subplots(figsize=(5.8, 5.2))
    axis.plot([0, 1], [0, 1], color="#6C757D", ls="--", label="Ideal")
    axis.plot(predicted, observed, color="#D1495B", marker="o", lw=2, label="Model")
    axis.set(
        xlabel="Predicted probability",
        ylabel="Observed frequency",
        title="Holdout calibration",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    axis.legend()
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def save_selective_plot(table: pd.DataFrame, destination: Path) -> None:
    figure, axis = plt.subplots(figsize=(6.8, 5.0))
    axis.plot(
        table["development_coverage"],
        table["development_error_rate"],
        color="#6C757D",
        marker="s",
        lw=1.8,
        label="Development OOF",
    )
    axis.plot(
        table["observed_coverage"],
        table["error_rate"],
        color="#00798C",
        marker="o",
        lw=2.2,
        label="Untouched holdout",
    )
    axis.fill_between(
        table["observed_coverage"],
        table["error_rate_ci_low"],
        table["error_rate_ci_high"],
        color="#00798C",
        alpha=0.15,
        label="Holdout Wilson 95% CI",
    )
    axis.set(
        xlabel="Coverage",
        ylabel="Error rate among predicted cases",
        title="Selective prediction: coverage versus risk",
        xlim=(0.55, 1.01),
    )
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def save_importance_plot(table: pd.DataFrame, destination: Path) -> None:
    top = table.head(12).sort_values("importance_mean")
    figure, axis = plt.subplots(figsize=(7.2, 5.2))
    axis.barh(top["feature"], top["importance_mean"], color="#D1495B")
    axis.set(
        xlabel="Decrease in holdout ROC AUC",
        title="Permutation importance",
    )
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def save_interval_plot(table: pd.DataFrame, destination: Path) -> None:
    wanted = [
        "roc_auc",
        "average_precision",
        "balanced_accuracy",
        "sensitivity",
        "specificity",
        "brier",
    ]
    plotted = table.set_index("metric").loc[wanted].reset_index()
    positions = np.arange(len(plotted))
    lower = plotted["estimate"] - plotted["ci_low"]
    upper = plotted["ci_high"] - plotted["estimate"]

    figure, axis = plt.subplots(figsize=(7.0, 4.8))
    axis.errorbar(
        plotted["estimate"],
        positions,
        xerr=np.vstack([lower, upper]),
        fmt="o",
        color="#182024",
        ecolor="#D1495B",
        capsize=4,
    )
    axis.set_yticks(positions, plotted["metric"])
    axis.invert_yaxis()
    axis.set(
        xlabel="Estimate with stratified bootstrap 95% CI",
        title="Untouched holdout uncertainty",
        xlim=(0, 1),
    )
    axis.grid(axis="x", alpha=0.2)
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def save_subgroup_plot(table: pd.DataFrame, destination: Path) -> None:
    labels = table["group"].str.replace("_", " ")
    positions = np.arange(len(table))
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    axes[0].barh(positions - 0.18, table["roc_auc"], height=0.34, label="ROC AUC")
    axes[0].barh(
        positions + 0.18,
        table["balanced_accuracy"],
        height=0.34,
        label="Balanced accuracy",
    )
    axes[0].set_yticks(positions, labels)
    axes[0].set_xlim(0.5, 0.9)
    axes[0].set_title("Group discrimination")
    axes[0].legend()
    axes[1].barh(
        positions - 0.18,
        table["selective_coverage"],
        height=0.34,
        color="#00798C",
        label="Coverage",
    )
    axes[1].barh(
        positions + 0.18,
        table["selective_error_rate"],
        height=0.34,
        color="#D1495B",
        label="Error rate",
    )
    axes[1].set_yticks(positions, labels)
    axes[1].set_xlim(0, 1)
    axes[1].set_title("80% policy by group")
    axes[1].legend()
    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def format_metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def format_metric_interval_row(
    metric: str,
    estimate: float,
    ci_low: float,
    ci_high: float,
) -> str:
    if metric == "ece_10":
        return f"| {metric} | {estimate:.4f} | not reported |"
    return (
        f"| {metric} | {estimate:.4f} | "
        f"[{ci_low:.4f}, {ci_high:.4f}] |"
    )


def write_report(
    *,
    source_raw: pd.DataFrame,
    modeling_raw: pd.DataFrame,
    invalid_counts: dict[str, int],
    duplicate_profile_rows: int,
    duplicate_profile_groups: int,
    conflicting_label_groups: int,
    development_results: dict,
    fold_results: pd.DataFrame,
    chosen_name: str,
    holdout_metrics: dict,
    metric_intervals: pd.DataFrame,
    selective: pd.DataFrame,
    subgroup: pd.DataFrame,
    error_summary: pd.DataFrame,
) -> None:
    development_rows = [
        f"| {name} | {result['metrics']['roc_auc']:.4f} | "
        f"{result['metrics']['average_precision']:.4f} | "
        f"{result['metrics']['brier']:.4f} | "
        f"{result['metrics']['ece_10']:.4f} |"
        for name, result in development_results.items()
    ]
    fold_stability = (
        fold_results.groupby("model")
        .agg(
            roc_auc_mean=("roc_auc", "mean"),
            roc_auc_std=("roc_auc", "std"),
            brier_mean=("brier", "mean"),
            brier_std=("brier", "std"),
        )
        .reset_index()
    )
    fold_rows = [
        f"| {row.model} | {row.roc_auc_mean:.4f} | {row.roc_auc_std:.4f} | "
        f"{row.brier_mean:.4f} | {row.brier_std:.4f} |"
        for row in fold_stability.itertuples(index=False)
    ]
    interval_rows = [
        format_metric_interval_row(
            row.metric,
            row.estimate,
            row.ci_low,
            row.ci_high,
        )
        for row in metric_intervals.itertuples(index=False)
    ]
    selective_rows = [
        f"| {row.target_coverage:.0%} | {row.observed_coverage:.1%} | "
        f"{row.error_rate:.4f} | "
        f"[{row.error_rate_ci_low:.4f}, {row.error_rate_ci_high:.4f}] | "
        f"{row.development_error_ci_high:.4f} | "
        f"{row.balanced_accuracy:.4f} |"
        for row in selective.itertuples(index=False)
    ]
    subgroup_rows = [
        f"| {row.group} | {row.n} | {row.roc_auc:.4f} | "
        f"{row.balanced_accuracy:.4f} | {row.brier:.4f} | "
        f"{row.selective_coverage:.1%} | {row.selective_error_rate:.4f} |"
        for row in subgroup.itertuples(index=False)
    ]
    error_rows = [
        f"| {row.outcome} | {row.n} | {row.mean_probability:.3f} | "
        f"{row.age_years_mean:.1f} | {row.systolic_bp_mean:.1f} | "
        f"{row.cholesterol_mean:.2f} |"
        for row in error_summary.itertuples(index=False)
    ]

    report = f"""# CardioTrust Validation Report

Generated by `python -m src.run_experiment`.

## Scope

CardioTrust is a Byte2Beat research prototype, not a diagnostic device. It
predicts the source dataset's binary `cardio` label and has no prospective or
external validation.

## Data integrity

- Source rows: {len(source_raw):,}
- Modeling rows after duplicate-profile exclusion: {len(modeling_raw):,}
- Rows excluded because their complete predictor profile was duplicated:
  {duplicate_profile_rows:,}
- Duplicate predictor-profile groups: {duplicate_profile_groups:,}
- Duplicate groups containing conflicting labels: {conflicting_label_groups:,}
- Positive prevalence after exclusion: {modeling_raw[TARGET].mean():.3%}
- Source missing values: {int(source_raw.isna().sum().sum()):,}
- Invalid age values: {invalid_counts['age']:,}
- Invalid height values: {invalid_counts['height']:,}
- Invalid weight values: {invalid_counts['weight']:,}
- Invalid blood-pressure rows: {invalid_counts['blood_pressure']:,}

All records belonging to a duplicated predictor profile are excluded from
modeling. This removes exact train/validation copies and ambiguous identical
profiles with discordant labels without choosing one label over another.
Plausibility rules are fixed and target-independent. Fold-specific imputers are
fit only on training data.

The host's processed file is not used for modeling. Its non-age columns match
the raw file, while age was min-max scaled before provenance was documented;
using the raw file keeps preprocessing inside validation.

## Validation design

- 80/20 stratified development/locked-holdout split with seed {HOLDOUT_SEED}
- {OOF_REPEATS} repeats of {OOF_FOLDS}-fold shuffled development validation
  with seed {SEED}
- three-fold sigmoid calibration inside every outer training fold
- model selection by Brier score from averaged repeated OOF probabilities
- fixed classification threshold of `0.5`
- abstention thresholds learned from development OOF confidence only
- one final holdout evaluation
- {BOOTSTRAP_ITERATIONS} stratified bootstrap iterations for metric uncertainty

## Development comparison

| Model | ROC AUC | Average precision | Brier | ECE |
|---|---:|---:|---:|---:|
{chr(10).join(development_rows)}

Selected model: **{chosen_name}**

| Model | Fold ROC AUC mean | Fold ROC AUC SD | Fold Brier mean | Fold Brier SD |
|---|---:|---:|---:|---:|
{chr(10).join(fold_rows)}

## Untouched holdout

| Metric | Estimate | Stratified bootstrap 95% CI |
|---|---:|---:|
{chr(10).join(interval_rows)}

Log loss: {holdout_metrics['log_loss']:.4f}; ECE (10 equal-width bins):
{holdout_metrics['ece_10']:.4f}.

The naive percentile-bootstrap ECE interval is omitted because resampled ECE
is upward-biased here: the generated percentile bounds do not contain the
point estimate. ECE is therefore treated as an exploratory calibration
summary, not a primary uncertainty claim.

## Selective prediction

The development error upper bound is descriptive. Threshold selection targets
coverage, not a guaranteed clinical risk level.

| Target coverage | Holdout coverage | Holdout error | Wilson 95% CI | Dev error upper 95% | Balanced accuracy |
|---:|---:|---:|---:|---:|---:|
{chr(10).join(selective_rows)}

## Subgroup audit

The final columns apply the single development-learned 80% coverage threshold
unchanged to every group. These results are descriptive, not fairness or
clinical-equivalence evidence.

| Group | N | ROC AUC | Balanced accuracy | Brier | Selective coverage | Selective error |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(subgroup_rows)}

## Error analysis

All values are aggregate holdout summaries; no row-level records are exported.

| Outcome | N | Mean probability | Mean age | Mean systolic BP | Mean cholesterol category |
|---|---:|---:|---:|---:|---:|
{chr(10).join(error_rows)}

## Limitations

- The upstream Kaggle Data Card displays the redistribution license as
  `Unknown`.
- Collection sites, dates, consent basis, cohort definition, and label
  construction are not documented by the host.
- Duplicate and conflicting profiles indicate label noise or data-generation
  ambiguity; excluding them avoids leakage but does not repair the source.
- There is no temporal, geographic, hospital, or prospective external
  validation.
- The abstention analysis is empirical and does not provide a clinical safety
  guarantee.
- The source two-category gender code is incomplete and must not be interpreted
  as a complete representation of sex or gender.
"""
    (REPORT_DIR / "baseline_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    source_raw = pd.read_csv(PRIMARY_DATA, sep=";")
    processed = pd.read_csv(PROCESSED_DATA, index_col=0)
    heart = pd.read_csv(HEART_DATA)

    if source_raw.shape != (70000, 13):
        raise ValueError(f"Unexpected primary-data shape: {source_raw.shape}")
    if processed.shape != source_raw.shape:
        raise ValueError(f"Unexpected processed-data shape: {processed.shape}")
    non_age_columns = [column for column in source_raw.columns if column != "age"]
    processed_non_age_match = all(
        np.array_equal(
            source_raw[column].to_numpy(),
            processed[column].to_numpy(),
        )
        for column in non_age_columns
    )
    if not processed_non_age_match:
        raise ValueError("Processed non-age columns do not align with raw data")
    if not (np.isclose(processed["age"].min(), 0.0) and np.isclose(
        processed["age"].max(),
        1.0,
    )):
        raise ValueError("Processed age column is not expected min-max scaling")

    predictor_columns = [
        column
        for column in source_raw.columns
        if column not in ("id", TARGET)
    ]
    duplicate_profile_mask = source_raw.duplicated(
        predictor_columns,
        keep=False,
    )
    duplicate_profile_rows = int(duplicate_profile_mask.sum())
    duplicate_profile_groups = int(
        source_raw.loc[duplicate_profile_mask]
        .groupby(predictor_columns, dropna=False)
        .ngroups
    )
    label_counts = source_raw.groupby(
        predictor_columns,
        dropna=False,
    )[TARGET].nunique()
    conflicting_label_groups = int((label_counts > 1).sum())
    modeling_raw = source_raw.loc[~duplicate_profile_mask].copy()

    _, source_invalid_counts = engineer_features(source_raw)
    features, modeling_invalid_counts = engineer_features(modeling_raw)
    target = modeling_raw[TARGET].astype(int).to_numpy()

    (
        x_development,
        x_holdout,
        y_development,
        y_holdout,
    ) = train_test_split(
        features,
        target,
        test_size=0.20,
        stratify=target,
        random_state=HOLDOUT_SEED,
    )

    models = build_models()
    development_results: dict[str, dict] = {}
    fold_tables = []
    for name, model in models.items():
        print(f"Repeated OOF probabilities: {name}", flush=True)
        probabilities, fold_table = repeated_oof_probabilities(
            model,
            x_development,
            y_development,
            folds=OOF_FOLDS,
            repeats=OOF_REPEATS,
            seed=SEED,
            n_jobs=OUTER_JOBS,
        )
        fold_table.insert(0, "model", name)
        fold_tables.append(fold_table)
        development_results[name] = {
            "probabilities": probabilities,
            "metrics": classification_metrics(
                y_development,
                probabilities,
                threshold=0.5,
            ),
        }
    fold_results = pd.concat(fold_tables, ignore_index=True)

    chosen_name = min(
        development_results,
        key=lambda name: development_results[name]["metrics"]["brier"],
    )
    chosen_development_probabilities = development_results[chosen_name][
        "probabilities"
    ]

    print(f"Fitting selected model: {chosen_name}", flush=True)
    final_model = clone(models[chosen_name])
    final_model.fit(x_development, y_development)
    holdout_probabilities = final_model.predict_proba(x_holdout)[:, 1]
    holdout_metrics = classification_metrics(
        y_holdout,
        holdout_probabilities,
        threshold=0.5,
    )

    selective = selective_table(
        y_development,
        chosen_development_probabilities,
        y_holdout,
        holdout_probabilities,
    )
    selective_confidence_threshold_80 = float(
        selective.loc[
            selective["target_coverage"] == 0.80,
            "confidence_threshold",
        ].iloc[0]
    )
    subgroup = subgroup_audit(
        x_holdout,
        y_holdout,
        holdout_probabilities,
        classification_threshold=0.5,
        confidence_threshold=selective_confidence_threshold_80,
    )
    metric_intervals = bootstrap_metric_intervals(
        y_holdout,
        holdout_probabilities,
        threshold=0.5,
        iterations=BOOTSTRAP_ITERATIONS,
        seed=SEED,
    )
    error_summary = error_profile_summary(
        x_holdout,
        y_holdout,
        holdout_probabilities,
        threshold=0.5,
    )
    reference_profile = build_reference_profile(
        modeling_raw.loc[x_development.index]
    )

    print("Computing permutation importance", flush=True)
    importance_size = min(5000, len(x_holdout))
    importance_positions = np.random.default_rng(SEED).choice(
        len(x_holdout),
        size=importance_size,
        replace=False,
    )
    importance_result = permutation_importance(
        final_model,
        x_holdout.iloc[importance_positions],
        y_holdout[importance_positions],
        scoring="roc_auc",
        n_repeats=5,
        random_state=SEED,
        n_jobs=1,
    )
    importance = (
        pd.DataFrame(
            {
                "feature": x_holdout.columns,
                "importance_mean": importance_result.importances_mean,
                "importance_std": importance_result.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )

    selective.to_csv(ARTIFACT_DIR / "selective_prediction.csv", index=False)
    subgroup.to_csv(ARTIFACT_DIR / "subgroup_audit.csv", index=False)
    importance.to_csv(ARTIFACT_DIR / "permutation_importance.csv", index=False)
    fold_results.to_csv(ARTIFACT_DIR / "cross_validation_folds.csv", index=False)
    metric_intervals.to_csv(ARTIFACT_DIR / "metric_intervals.csv", index=False)
    error_summary.to_csv(ARTIFACT_DIR / "error_analysis.csv", index=False)

    joblib.dump(
        {
            "model": final_model,
            "feature_columns": list(features.columns),
            "classification_threshold": 0.5,
            "selective_confidence_threshold_80": selective_confidence_threshold_80,
            "reference_profile": reference_profile,
            "source": "cardio_base.csv",
            "modeling_rows": len(modeling_raw),
            "excluded_duplicate_profile_rows": duplicate_profile_rows,
            "seed": SEED,
            "holdout_seed": HOLDOUT_SEED,
            "model_version": "2.0",
        },
        ARTIFACT_DIR / "model.joblib",
    )

    data_manifest = {
        "files": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in (PRIMARY_DATA, PROCESSED_DATA, HEART_DATA)
        },
        "primary_shape": list(source_raw.shape),
        "modeling_shape": list(modeling_raw.shape),
        "processed_shape": list(processed.shape),
        "heart_shape": list(heart.shape),
        "primary_columns": list(source_raw.columns),
        "source_invalid_counts": source_invalid_counts,
        "modeling_invalid_counts": modeling_invalid_counts,
        "duplicate_profile_rows_excluded": duplicate_profile_rows,
        "duplicate_profile_groups": duplicate_profile_groups,
        "conflicting_label_groups": conflicting_label_groups,
        "processed_non_age_columns_match": processed_non_age_match,
        "processed_age_range": [
            float(processed["age"].min()),
            float(processed["age"].max()),
        ],
        "processed_file_used_for_modeling": False,
    }
    (ARTIFACT_DIR / "data_manifest.json").write_text(
        json.dumps(data_manifest, indent=2),
        encoding="utf-8",
    )

    interval_lookup = {
        row.metric: {
            "estimate": row.estimate,
            "ci_low": row.ci_low,
            "ci_high": row.ci_high,
        }
        for row in metric_intervals.itertuples(index=False)
    }
    result_summary = {
        "selected_model": chosen_name,
        "development": {
            name: result["metrics"]
            for name, result in development_results.items()
        },
        "holdout_at_0_5": holdout_metrics,
        "holdout_intervals_95": interval_lookup,
        "split": {
            "source_rows": len(source_raw),
            "excluded_duplicate_profile_rows": duplicate_profile_rows,
            "modeling_rows": len(modeling_raw),
            "development_rows": len(x_development),
            "holdout_rows": len(x_holdout),
            "holdout_seed": HOLDOUT_SEED,
            "development_seed": SEED,
        },
        "validation": {
            "outer_folds": OOF_FOLDS,
            "outer_repeats": OOF_REPEATS,
            "inner_calibration_folds": 3,
            "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
            "outer_jobs": OUTER_JOBS,
            "classification_threshold": 0.5,
            "selective_target_coverage": 0.80,
            "selective_confidence_threshold": selective_confidence_threshold_80,
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    (ARTIFACT_DIR / "metrics.json").write_text(
        json.dumps(result_summary, indent=2),
        encoding="utf-8",
    )

    save_roc_pr_plot(
        y_holdout,
        holdout_probabilities,
        FIGURE_DIR / "roc_pr.png",
    )
    save_calibration_plot(
        y_holdout,
        holdout_probabilities,
        FIGURE_DIR / "calibration.png",
    )
    save_selective_plot(
        selective,
        FIGURE_DIR / "coverage_risk.png",
    )
    save_importance_plot(
        importance,
        FIGURE_DIR / "permutation_importance.png",
    )
    save_interval_plot(
        metric_intervals,
        FIGURE_DIR / "holdout_intervals.png",
    )
    save_subgroup_plot(
        subgroup,
        FIGURE_DIR / "subgroup_performance.png",
    )
    write_report(
        source_raw=source_raw,
        modeling_raw=modeling_raw,
        invalid_counts=source_invalid_counts,
        duplicate_profile_rows=duplicate_profile_rows,
        duplicate_profile_groups=duplicate_profile_groups,
        conflicting_label_groups=conflicting_label_groups,
        development_results=development_results,
        fold_results=fold_results,
        chosen_name=chosen_name,
        holdout_metrics=holdout_metrics,
        metric_intervals=metric_intervals,
        selective=selective,
        subgroup=subgroup,
        error_summary=error_summary,
    )

    print(json.dumps(result_summary, indent=2), flush=True)


if __name__ == "__main__":
    main()

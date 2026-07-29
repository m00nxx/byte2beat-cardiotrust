from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.features import engineer_features


PROFILE_FIELDS = (
    "age_years",
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "glucose",
    "smoke",
    "alcohol",
    "active",
)

FIELD_LABELS = {
    "age_years": "Age",
    "gender": "Source gender category",
    "height": "Height",
    "weight": "Weight",
    "ap_hi": "Systolic pressure",
    "ap_lo": "Diastolic pressure",
    "cholesterol": "Cholesterol category",
    "glucose": "Glucose category",
    "smoke": "Smoking",
    "alcohol": "Alcohol intake",
    "active": "Physical activity",
}


def profile_to_raw_frame(profile: dict[str, float | int]) -> pd.DataFrame:
    missing = [field for field in PROFILE_FIELDS if field not in profile]
    if missing:
        raise ValueError(f"Missing profile fields: {', '.join(missing)}")
    numeric_values = [profile[field] for field in PROFILE_FIELDS]
    if not all(np.isfinite(float(value)) for value in numeric_values):
        raise ValueError("Profile values must be finite numbers")

    categories = {
        "gender": {1, 2},
        "cholesterol": {1, 2, 3},
        "glucose": {1, 2, 3},
        "smoke": {0, 1},
        "alcohol": {0, 1},
        "active": {0, 1},
    }
    invalid_categories = [
        field
        for field, allowed in categories.items()
        if profile[field] not in allowed
    ]
    if invalid_categories:
        raise ValueError(
            "Invalid categorical values: " + ", ".join(invalid_categories)
        )

    return pd.DataFrame(
        [
            {
                "age": float(profile["age_years"]) * 365.25,
                "gender": int(profile["gender"]),
                "height": float(profile["height"]),
                "weight": float(profile["weight"]),
                "ap_hi": float(profile["ap_hi"]),
                "ap_lo": float(profile["ap_lo"]),
                "cholesterol": int(profile["cholesterol"]),
                "gluc": int(profile["glucose"]),
                "smoke": int(profile["smoke"]),
                "alco": int(profile["alcohol"]),
                "active": int(profile["active"]),
            }
        ]
    )


def _probability(profile: dict[str, float | int], bundle: dict[str, Any]) -> float:
    features, _ = engineer_features(profile_to_raw_frame(profile))
    features = features.loc[:, bundle["feature_columns"]]
    return float(bundle["model"].predict_proba(features)[0, 1])


def predict_profile(
    profile: dict[str, float | int],
    bundle: dict[str, Any],
) -> dict[str, Any]:
    raw = profile_to_raw_frame(profile)
    features, invalid_counts = engineer_features(raw)
    features = features.loc[:, bundle["feature_columns"]]
    probability = float(bundle["model"].predict_proba(features)[0, 1])
    confidence = max(probability, 1.0 - probability)
    confidence_threshold = float(
        bundle.get("selective_confidence_threshold_80", 0.6063053741431872)
    )

    invalid_inputs = [
        name
        for name in ("age", "height", "weight", "blood_pressure")
        if invalid_counts[name] > 0
    ]
    if invalid_inputs:
        decision = "check_input"
    elif confidence < confidence_threshold:
        decision = "review"
    elif probability >= 0.5:
        decision = "model_positive"
    else:
        decision = "model_negative"

    return {
        "probability": probability,
        "confidence": confidence,
        "confidence_threshold": confidence_threshold,
        "decision": decision,
        "invalid_inputs": invalid_inputs,
    }


def local_sensitivity(
    profile: dict[str, float | int],
    bundle: dict[str, Any],
) -> pd.DataFrame:
    reference = bundle.get("reference_profile")
    if not reference:
        raise ValueError("The model bundle does not contain a reference profile")

    baseline = _probability(profile, bundle)
    rows = []
    for field in PROFILE_FIELDS:
        alternate = dict(profile)
        alternate[field] = reference[field]
        reference_probability = _probability(alternate, bundle)
        rows.append(
            {
                "feature": FIELD_LABELS[field],
                "delta_probability": baseline - reference_probability,
                "absolute_delta": abs(baseline - reference_probability),
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("absolute_delta", ascending=False)
        .drop(columns="absolute_delta")
        .reset_index(drop=True)
    )

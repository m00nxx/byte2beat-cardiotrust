from __future__ import annotations

import numpy as np
import pandas as pd


AGE_MIN_YEARS = 29.0
AGE_MAX_YEARS = 65.0


def engineer_features(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    frame = raw.copy()

    invalid = {
        "age": ~frame["age"].between(
            AGE_MIN_YEARS * 365.25,
            AGE_MAX_YEARS * 365.25,
        ),
        "height": ~frame["height"].between(120, 220),
        "weight": ~frame["weight"].between(30, 250),
        "systolic": ~frame["ap_hi"].between(70, 250),
        "diastolic": ~frame["ap_lo"].between(40, 150),
        "bp_order": frame["ap_hi"] <= frame["ap_lo"],
    }
    invalid["blood_pressure"] = (
        invalid["systolic"] | invalid["diastolic"] | invalid["bp_order"]
    )

    height = frame["height"].mask(invalid["height"])
    weight = frame["weight"].mask(invalid["weight"])
    systolic = frame["ap_hi"].mask(invalid["blood_pressure"])
    diastolic = frame["ap_lo"].mask(invalid["blood_pressure"])

    features = pd.DataFrame(index=frame.index)
    features["age_years"] = (frame["age"] / 365.25).mask(invalid["age"])
    features["gender"] = frame["gender"]
    features["height_cm"] = height
    features["weight_kg"] = weight
    features["bmi"] = weight / np.square(height / 100.0)
    features["systolic_bp"] = systolic
    features["diastolic_bp"] = diastolic
    features["pulse_pressure"] = systolic - diastolic
    features["mean_arterial_pressure"] = (systolic + 2.0 * diastolic) / 3.0
    features["cholesterol"] = frame["cholesterol"]
    features["glucose"] = frame["gluc"]
    features["smoker"] = frame["smoke"]
    features["alcohol"] = frame["alco"]
    features["active"] = frame["active"]
    features["invalid_age"] = invalid["age"].astype(int)
    features["invalid_height"] = invalid["height"].astype(int)
    features["invalid_weight"] = invalid["weight"].astype(int)
    features["invalid_blood_pressure"] = invalid["blood_pressure"].astype(int)

    counts = {name: int(mask.sum()) for name, mask in invalid.items()}
    return features, counts


def build_reference_profile(raw_development: pd.DataFrame) -> dict[str, float | int]:
    categorical = ("gender", "cholesterol", "gluc", "smoke", "alco", "active")
    profile: dict[str, float | int] = {
        "age_years": float(np.median(raw_development["age"]) / 365.25),
        "height": float(np.median(raw_development["height"])),
        "weight": float(np.median(raw_development["weight"])),
        "ap_hi": float(np.median(raw_development["ap_hi"])),
        "ap_lo": float(np.median(raw_development["ap_lo"])),
    }
    for field in categorical:
        output_name = {"gluc": "glucose", "alco": "alcohol"}.get(field, field)
        profile[output_name] = int(raw_development[field].mode().iloc[0])
    return profile

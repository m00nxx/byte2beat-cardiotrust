from __future__ import annotations

import unittest

import numpy as np

from src.inference import predict_profile, profile_to_raw_frame
from src.features import engineer_features


class ConstantModel:
    def __init__(self, probability: float) -> None:
        self.probability = probability

    def predict_proba(self, features):
        return np.tile([1.0 - self.probability, self.probability], (len(features), 1))


VALID_PROFILE = {
    "age_years": 55,
    "gender": 1,
    "height": 165,
    "weight": 72,
    "ap_hi": 130,
    "ap_lo": 80,
    "cholesterol": 1,
    "glucose": 1,
    "smoke": 0,
    "alcohol": 0,
    "active": 1,
}


class InferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        features, _ = engineer_features(profile_to_raw_frame(VALID_PROFILE))
        self.bundle = {
            "model": ConstantModel(0.82),
            "feature_columns": list(features.columns),
            "selective_confidence_threshold_80": 0.61,
        }

    def test_valid_high_confidence_profile_gets_model_label(self) -> None:
        result = predict_profile(VALID_PROFILE, self.bundle)
        self.assertEqual(result["decision"], "model_positive")
        self.assertEqual(result["invalid_inputs"], [])

    def test_low_confidence_profile_is_withheld(self) -> None:
        self.bundle["model"] = ConstantModel(0.53)
        result = predict_profile(VALID_PROFILE, self.bundle)
        self.assertEqual(result["decision"], "review")

    def test_implausible_blood_pressure_overrides_high_confidence(self) -> None:
        profile = dict(VALID_PROFILE, ap_hi=80, ap_lo=120)
        result = predict_profile(profile, self.bundle)
        self.assertEqual(result["decision"], "check_input")
        self.assertIn("blood_pressure", result["invalid_inputs"])

    def test_age_outside_source_range_is_withheld(self) -> None:
        profile = dict(VALID_PROFILE, age_years=75)
        result = predict_profile(profile, self.bundle)
        self.assertEqual(result["decision"], "check_input")
        self.assertIn("age", result["invalid_inputs"])

    def test_non_finite_value_is_rejected(self) -> None:
        profile = dict(VALID_PROFILE, weight=np.nan)
        with self.assertRaisesRegex(ValueError, "finite"):
            profile_to_raw_frame(profile)

    def test_invalid_category_is_rejected(self) -> None:
        profile = dict(VALID_PROFILE, gender=3)
        with self.assertRaisesRegex(ValueError, "gender"):
            profile_to_raw_frame(profile)


if __name__ == "__main__":
    unittest.main()

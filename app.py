from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from src.inference import local_sensitivity, predict_profile


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "artifacts" / "model.joblib"
METRICS_PATH = ROOT / "artifacts" / "metrics.json"
IMPORTANCE_PATH = ROOT / "artifacts" / "permutation_importance.csv"


st.set_page_config(
    page_title="CardioTrust / Byte2Beat",
    page_icon="CT",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #182024;
        --paper: #f2efe8;
        --signal: #d84a2f;
        --aqua: #087f8c;
        --line: rgba(24, 32, 36, 0.18);
    }
    .stApp {
        color: var(--ink);
        background:
            linear-gradient(rgba(24,32,36,.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(24,32,36,.045) 1px, transparent 1px),
            radial-gradient(circle at 82% 8%, rgba(216,74,47,.15), transparent 28rem),
            var(--paper);
        background-size: 28px 28px, 28px 28px, auto, auto;
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1180px; padding-top: 2.8rem; }
    h1, h2, h3 {
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: -0.035em;
    }
    p, label, [data-testid="stMetricLabel"] {
        font-family: "Cascadia Mono", "Courier New", monospace;
    }
    .eyebrow {
        color: var(--signal);
        font: 700 .75rem/1 "Cascadia Mono", monospace;
        letter-spacing: .18em;
        text-transform: uppercase;
        margin-bottom: .8rem;
    }
    .hero {
        border-top: 5px solid var(--ink);
        border-bottom: 1px solid var(--line);
        padding: 1.2rem 0 1.7rem;
        margin-bottom: 1.6rem;
    }
    .hero h1 {
        font-size: clamp(3.2rem, 8vw, 7rem);
        line-height: .82;
        margin: 0;
    }
    .hero p { max-width: 760px; font-size: .92rem; margin-top: 1.5rem; }
    .stamp {
        border: 1px solid var(--line);
        border-left: 7px solid var(--aqua);
        background: rgba(255,255,255,.48);
        padding: 1.2rem 1.3rem;
        margin: .4rem 0 1.4rem;
    }
    .stamp.review { border-left-color: #d79b19; }
    .stamp.alert { border-left-color: var(--signal); }
    .stamp strong {
        display: block;
        font: 700 .72rem/1 "Cascadia Mono", monospace;
        letter-spacing: .15em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }
    [data-testid="stForm"] {
        border: 1px solid var(--line);
        border-radius: 0;
        background: rgba(255,255,255,.38);
    }
    [data-testid="stMetric"] {
        border-top: 3px solid var(--ink);
        padding-top: .65rem;
    }
    .stButton > button, .stFormSubmitButton > button {
        border-radius: 0;
        border: 2px solid var(--ink);
        background: var(--ink);
        color: var(--paper);
        font-family: "Cascadia Mono", monospace;
        font-weight: 700;
        min-height: 3rem;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        border-color: var(--signal);
        background: var(--signal);
        color: white;
    }
    .disclaimer {
        border-top: 1px solid var(--line);
        margin-top: 2rem;
        padding-top: 1rem;
        color: rgba(24,32,36,.72);
        font: .76rem/1.55 "Cascadia Mono", monospace;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_bundle() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Missing artifacts/model.joblib. Run: python -m src.run_experiment"
        )
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_evidence() -> tuple[dict, pd.DataFrame]:
    return (
        json.loads(METRICS_PATH.read_text(encoding="utf-8")),
        pd.read_csv(IMPORTANCE_PATH),
    )


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Byte2Beat / Research prototype 02</div>
      <h1>Cardio<br>Trust</h1>
      <p>
        A calibrated cardiovascular-label model that can decline to classify.
        The interface makes uncertainty and input-quality failures visible
        instead of hiding them behind a binary answer.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    bundle = load_bundle()
    metrics, importance = load_evidence()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

summary_columns = st.columns(4)
summary_columns[0].metric("Holdout ROC AUC", f"{metrics['holdout_at_0_5']['roc_auc']:.3f}")
summary_columns[1].metric("Brier score", f"{metrics['holdout_at_0_5']['brier']:.3f}")
summary_columns[2].metric("Calibration ECE", f"{metrics['holdout_at_0_5']['ece_10']:.3f}")
summary_columns[3].metric("Untouched holdout", f"{metrics['split']['holdout_rows']:,}")
roc_interval = metrics["holdout_intervals_95"]["roc_auc"]
st.caption(
    "Locked holdout ROC AUC 95% stratified-bootstrap interval: "
    f"{roc_interval['ci_low']:.3f}-{roc_interval['ci_high']:.3f}. "
    "The final protocol was frozen before this holdout was observed."
)

st.subheader("Profile input")
st.caption(
    "Values mirror the source dataset. Gender categories are retained only as "
    "opaque source codes; they are not a complete representation of sex or gender."
)

with st.form("profile"):
    first, second, third = st.columns(3)
    with first:
        age_years = st.number_input("Age (years)", 0, 120, 55)
        gender = st.selectbox(
            "Source gender category",
            options=(1, 2),
            format_func=lambda value: f"Category {value}",
        )
        height = st.number_input("Height (cm)", 80, 250, 165)
        weight = st.number_input("Weight (kg)", 20.0, 300.0, 72.0, step=0.5)
    with second:
        ap_hi = st.number_input("Systolic pressure", -200, 20000, 130)
        ap_lo = st.number_input("Diastolic pressure", -100, 12000, 80)
        cholesterol = st.select_slider(
            "Cholesterol category",
            options=(1, 2, 3),
            format_func=lambda value: ("Normal", "Above normal", "Well above normal")[
                value - 1
            ],
        )
        glucose = st.select_slider(
            "Glucose category",
            options=(1, 2, 3),
            format_func=lambda value: ("Normal", "Above normal", "Well above normal")[
                value - 1
            ],
        )
    with third:
        smoke = int(st.toggle("Smoking"))
        alcohol = int(st.toggle("Alcohol intake"))
        active = int(st.toggle("Physical activity", value=True))
        st.markdown(
            """
            **Decision policy**

            The demo withholds a label for implausible measurements or when
            model confidence is below the development-set 80% coverage threshold.
            """
        )
    submitted = st.form_submit_button("Evaluate model signal", use_container_width=True)

if submitted:
    profile = {
        "age_years": age_years,
        "gender": gender,
        "height": height,
        "weight": weight,
        "ap_hi": ap_hi,
        "ap_lo": ap_lo,
        "cholesterol": cholesterol,
        "glucose": glucose,
        "smoke": smoke,
        "alcohol": alcohol,
        "active": active,
    }
    result = predict_profile(profile, bundle)

    if result["decision"] == "check_input":
        invalid_labels = {
            "age": "age",
            "height": "height",
            "weight": "weight",
            "blood_pressure": "blood pressure",
        }
        invalid = ", ".join(
            invalid_labels[field] for field in result["invalid_inputs"]
        )
        st.markdown(
            f"""
            <div class="stamp alert">
              <strong>Input check required</strong>
              No model label is shown. Implausible field group(s): {invalid}.
              Correct the measurements before interpreting any output.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif result["decision"] == "review":
        st.markdown(
            """
            <div class="stamp review">
              <strong>Escalate / abstain</strong>
              The profile falls inside the model's uncertainty region.
              CardioTrust intentionally withholds a binary label.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        direction = (
            "leans toward source label 1"
            if result["decision"] == "model_positive"
            else "leans toward source label 0"
        )
        st.markdown(
            f"""
            <div class="stamp">
              <strong>Model signal</strong>
              The calibrated model {direction}. This is a dataset-label
              prediction, not a diagnosis or individual risk estimate.
            </div>
            """,
            unsafe_allow_html=True,
        )

    if result["decision"] != "check_input":
        output_columns = st.columns(3)
        output_columns[0].metric(
            "P(source label = 1)",
            f"{result['probability']:.1%}",
        )
        output_columns[1].metric("Model confidence", f"{result['confidence']:.1%}")
        output_columns[2].metric(
            "Required confidence",
            f"{result['confidence_threshold']:.1%}",
        )

        st.subheader("Profile sensitivity")
        st.caption(
            "Change in model probability attributable to replacing one entered "
            "value with the development-set reference value. This is sensitivity "
            "analysis, not a causal explanation."
        )
        sensitivity = local_sensitivity(profile, bundle).head(8).set_index("feature")
        st.bar_chart(
            sensitivity,
            horizontal=True,
            color="#d84a2f",
            x_label="Probability delta versus reference",
            y_label="Input",
        )

st.subheader("Global holdout evidence")
evidence_left, evidence_right = st.columns([1.2, 1])
with evidence_left:
    st.image(
        str(ROOT / "artifacts" / "figures" / "coverage_risk.png"),
        caption="Observed holdout error falls as the model abstains more often.",
    )
with evidence_right:
    top_importance = (
        importance.head(8)
        .sort_values("importance_mean")
        .set_index("feature")[["importance_mean"]]
    )
    st.bar_chart(
        top_importance,
        horizontal=True,
        color="#087f8c",
        x_label="Holdout ROC AUC decrease",
        y_label="Feature",
    )

intervals, subgroups = st.columns(2)
with intervals:
    st.image(
        str(ROOT / "artifacts" / "figures" / "holdout_intervals.png"),
        caption="Locked-holdout estimates and 95% bootstrap intervals.",
    )
with subgroups:
    st.image(
        str(ROOT / "artifacts" / "figures" / "subgroup_performance.png"),
        caption="Performance and selective coverage vary materially by age group.",
    )

st.markdown(
    """
    <div class="disclaimer">
      RESEARCH USE ONLY / NOT A MEDICAL DEVICE. Trained on a single public
      tabular dataset with unknown redistribution license and no external,
      temporal, geographic, hospital, or prospective validation. Performance
      is weakest in the source age-60-plus subgroup, where the fixed selective
      policy covers only 65.0% of holdout records. All 82 records belonging to
      duplicated predictor profiles were excluded before splitting. Do not use
      for diagnosis, treatment, triage, or emergency decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

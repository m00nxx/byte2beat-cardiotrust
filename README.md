# CardioTrust / Byte2Beat

Local project for the [Byte2Beat Kaggle Community Hackathon](https://www.kaggle.com/competitions/byte-2-beat).

Status on 2026-07-29: **CONDITIONAL GO**. A validation-locked prototype exists,
replays deterministically, and now runs in a real private Coder workspace.
Publication remains blocked by unresolved dataset licensing and prize
administration. An authenticated 100-second Coder demo is recorded. Cash
eligibility remains unproven until organizer acceptance of the local deployment
form is known.

## Live competition status

- Rules accepted and hackathon joined on 2026-07-27.
- Kaggle confirmed the exact deadline as `2026-08-01 09:00 CEST`
  (`2026-08-01 07:00 UTC`) in the joined account on 2026-07-27.
- Kaggle reconfirmed the deadline as `2026-08-01 09:00 CEST` in the joined
  account on 2026-07-29. An organizer also identified Kaggle as the source of
  the most up-to-date rules.
- The live Devpost page reported on 2026-07-29 that the hackathon had been
  removed. This is treated as a prize-administration risk, not as a replacement
  deadline.
- The acceptance flow did not request phone verification.
- Participation was 339 entrants immediately after acceptance.
- No writeup, notebook, public demo, or final submission has been created.
- The published rules still contain unfilled `[INSERT]` placeholders.
- Organizers stated that all USD 1,500 of cash prizes require deployment
  through Coder.
- The official Discord was joined read-only. No challenge-specific Coder guide
  or public deployment template was found, and no organizer was contacted.
- A self-hosted Coder v2.35.3 workspace now runs the private model and app.
  Preflight passed, all 13 tests passed, and Streamlit reported healthy.
- Coder detected port 8501 and kept it authenticated and owner-only. No trial,
  public endpoint, or shared port was created.
- A 100-second authenticated recording demonstrates the Coder workspace,
  owner-only port proxy, three decision outcomes, and model limitations.

The judged entry must include a submitted Kaggle Writeup, selected track,
public notebook, public project or demo, and written report. A draft writeup is
not a submission. Public-writeup attachments may become public after the
deadline.

## Project

**CardioTrust** is a calibrated cardiovascular-label model that can withhold a
binary answer. It combines:

- fixed, target-independent plausibility checks
- logistic and nonlinear model comparison
- nested probability calibration
- 3 repeats of 5-fold out-of-fold development validation
- a protocol-locked 20% final holdout
- a development-learned selective-prediction threshold
- subgroup, calibration, permutation-importance, and sensitivity evidence
- a non-diagnostic Streamlit demo

The app blocks implausible anthropometric or blood-pressure inputs and abstains
when confidence is below the development-set threshold corresponding to 80%
target coverage.

## Baseline result

The selected model is a sigmoid-calibrated histogram gradient booster.

| Holdout metric | Result |
|---|---:|
| ROC AUC | 0.8014 [0.7942, 0.8087] |
| Average precision | 0.7865 [0.7765, 0.7960] |
| Balanced accuracy at 0.5 | 0.7349 [0.7279, 0.7429] |
| Brier score | 0.1806 [0.1771, 0.1841] |
| Log loss | 0.5412 [0.5330, 0.5496] |
| ECE, 10 bins | 0.0026 (exploratory) |

At approximately 80% observed coverage, the holdout error rate decreases from
0.2651 to 0.2207 and balanced accuracy increases from 0.7349 to 0.7794.
This is an empirical selective-prediction result, not a clinical safety
guarantee.

Performance is materially weaker for the source age-60-plus subgroup:
ROC AUC 0.7102 and balanced accuracy 0.6068 on 2,538 holdout records. Its
selective coverage is only 65.0% under the global policy. This is prominent in
the writeup and demo.

## Reproduce

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.run_experiment
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The final protocol and code hashes were frozen before observing the holdout.
A second full run from the pinned environment produced byte-identical
`metrics.json`, selective-policy, subgroup, fold, and interval artifacts.

The Dev Container includes Coder autostart metadata, a private demo app, an
idempotent Streamlit launcher, and a health check. Separately, the project has
been demonstrated in a real self-hosted Coder workspace using the Docker
Containers template and Git Clone module. This proves actual local Coder
execution, but not organizer acceptance or cash-prize eligibility.

The Discord evidence and exact operational interpretation are recorded in
`docs/discord_coder_evidence_2026-07-29.md`.
The live local deployment evidence is recorded in
`docs/coder_local_deployment_2026-07-29.md`.

`artifacts/model.joblib` remains private and excluded from version control. A
clean Coder clone requires that exact file to be transferred into the workspace
before startup. `python scripts/coder_preflight.py` verifies its locked hash,
the required evidence files, and owner-only app access.

## Key artifacts

- `app.py`: interactive selective-prediction demo
- `src/run_experiment.py`: deterministic training and evaluation
- `src/features.py`: shared plausibility and feature engineering
- `src/inference.py`: demo decision policy and profile sensitivity
- `reports/baseline_report.md`: generated technical result
- `reports/writeup_draft.md`: local, non-submitted narrative
- `notebooks/cardio_trust.ipynb`: clean local notebook draft
- `docs/VALIDATION_LOCK.md`: protocol freeze and locked code hashes
- `docs/MODEL_CARD.md`: intended use, metrics, and limitations
- `docs/CODER_DEMO_PLAN.md`: required Coder recording evidence
- `docs/coder_local_deployment_2026-07-29.md`: actual Coder workspace evidence
- `artifacts/recordings/coder_demo_final.mp4`: authenticated Coder demo
- `artifacts/figures/coder_app_model_signal.png`: proxied app evidence
- `artifacts/figures/coder_app_limitations.png`: subgroup-limit evidence
- `artifacts/model_manifest.json`: private model size and locked SHA-256
- `scripts/coder_preflight.py`: fail-closed Coder deployment validation
- `scripts/start_local_coder_server.sh`: foreground local Coder control plane
- `scripts/serve_local_repo.sh`: foreground private Git source for the template
- `artifacts/metrics.json`: exact model metrics and environment
- `artifacts/data_manifest.json`: file hashes, shapes, and anomaly counts
- `artifacts/figures/demo_desktop.png`: visually inspected demo render
- `tests/`: evaluation, abstention, and input-quality tests

## Data and publication gate

Three host-provided tabular CSVs were downloaded locally. The 627 MB ECG file
was deliberately excluded because the tabular route was sufficient.

The primary 70,000-row file appears to derive from Svetlana Ulianova's Kaggle
Cardiovascular Disease dataset: dimensions, columns, encodings, and preview
records match. The upstream Kaggle Data Card reports the license as `Unknown`.
Therefore:

- raw and transformed row-level data are excluded from version control
- no dataset redistribution is authorized by this repository
- provenance and license must be clarified before any public release
- trained-model publication also needs a deliberate legal review

See `PROVENANCE.md` for exact source IDs, sizes, hashes, and the evidence limit.

## Remaining external gates

Separate user approval is required before:

- contacting the organizer or sending any Discord message
- starting a Coder trial or provisioning paid resources
- publishing a repository, Kaggle notebook, demo, or writeup
- exposing a trained model or any dataset-derived artifact publicly
- making the one final hackathon submission

No final submission has been made.

# Byte2Beat Submission Checklist

Status date: 2026-07-29. Checked items have local evidence; they do not imply
organizer acceptance or a final submission.

## Entry gate

- [x] Preserve a dated evidence note for the visible rules
- [ ] Resolve or consciously accept the remaining `[INSERT]` placeholders
- [ ] Confirm participant age and jurisdiction eligibility
- [x] Join the hackathon
- [x] Record that phone verification was not requested
- [x] Accept the rules
- [x] Confirm `2026-08-01 07:00 UTC` / `09:00 CEST` in the joined account
- [x] Resolve the operative deadline in favor of fresh Kaggle evidence
- [x] Reconfirm `2026-08-01 09:00 CEST` in the joined Kaggle account
- [ ] Accept or clarify the remaining Devpost prize-administration risk

## Data gate

- [x] Download only the selected host-provided tabular datasets
- [x] Record source IDs, names, byte sizes, and SHA-256 hashes
- [x] Inspect schema, missingness, duplicates, balance, and implausible values
- [x] Exclude the unnecessary 627 MB ECG dataset
- [ ] Obtain or verify an upstream redistribution license
- [ ] Confirm that publication of transformed data and the trained model is permitted

## Modeling

- [x] Pin the environment and random seed
- [x] Three repeats of five-fold stratified OOF development validation
- [x] Exclude every duplicated predictor profile before splitting
- [x] Logistic baseline
- [x] Nonlinear tree baseline
- [x] Nested sigmoid probability calibration
- [x] Development-learned selective-prediction policy
- [x] Coverage-risk curve
- [x] Subgroup audit
- [x] Global permutation importance
- [x] Per-profile sensitivity explanation
- [x] One untouched final holdout evaluation
- [x] Freeze protocol and code hashes before final holdout observation
- [x] Bootstrap intervals and Wilson selective-error intervals
- [x] Aggregate error-profile analysis
- [x] Byte-identical metrics/selective/subgroup/folds/intervals replay

## Deliverables

- [x] Clean local notebook draft
- [ ] Clean public Kaggle notebook
- [ ] Public repository with setup instructions
- [x] Interactive demo implemented and locally tested
- [x] Dev Container/Coder-compatible workspace scaffold
- [x] Coder app metadata, autostart launcher, and health check
- [x] Fail-closed Coder preflight for the private model hash and app visibility
- [x] Record the exact private model transfer requirement
- [x] Join the official Discord and review Coder guidance read-only
- [x] Record organizer evidence that cash requires deployment through Coder
- [x] Record that no challenge-specific Coder deployment guide was found
- [x] Run the project in a real self-hosted Coder workspace
- [x] Verify the private model, 13 tests, and Streamlit health inside Coder
- [x] Keep the Coder application port owner-only
- [x] Coder integration visibly demonstrated and documented
- [x] Record the authenticated local Coder demo video
- [x] Ask the organizer whether the local Coder recording satisfies cash eligibility
- [ ] Receive and record the organizer response
- [ ] Confirm organizer acceptance of a self-hosted, locally reachable deployment
- [x] Written technical report
- [x] Local Kaggle Writeup draft
- [ ] Kaggle Writeup created with track selected
- [x] Medical limitations and non-diagnostic disclaimer
- [ ] All eventual public links work without login or paywall

## Final gate

- [x] Re-run experiment from the pinned local environment
- [x] Verify metrics and figures against saved outputs
- [x] Record that private Kaggle attachments may become public after deadline
- [x] Keep local copies of all current artifacts
- [ ] User reviews the final package
- [ ] User gives separate approval for publication
- [ ] User gives separate approval for final submission

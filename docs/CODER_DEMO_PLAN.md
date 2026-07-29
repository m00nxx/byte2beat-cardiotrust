# Coder Demo Evidence Plan

Status date: 2026-07-29  
Status: organizer requirement confirmed; Coder-native configuration prepared;
live Coder execution not yet demonstrated

## Confirmed organizer requirement

A read-only review of the official Hack4Health Discord found organizer
statements that:

- Coder sponsors all USD 1,500 of the cash prizes
- cash eligibility requires deploying the code through Coder
- a visual website developed through Coder is a recommended integration
- Google Sites is not an acceptable substitute
- entries without Coder remain eligible for non-cash prizes

No challenge-specific Coder guide, public template, or deployment URL was
visible in the inspected channels and indexed searches. See
`docs/discord_coder_evidence_2026-07-29.md`.

## Implemented integration

The repository contains a Linux Dev Container that:

- installs the pinned Python environment
- starts Streamlit idempotently on workspace start
- exposes a private-owner Coder app named `CardioTrust Demo`
- health-checks `/_stcore/health`
- retains web terminal, SSH, port forwarding, and VS Code access

Coder requires version 2.24 or newer, Docker inside the workspace, and the
Dev Containers CLI. Autostart also depends on the template administrator
enabling Coder's discovery-autostart setting.

## Required recording

1. Open the repository in an eligible Coder workspace.
2. Transfer the private `artifacts/model.joblib` into the cloned workspace.
3. Run `python scripts/coder_preflight.py` and capture the expected hash and
   `preflight: PASS`.
4. Capture Coder discovering and auto-starting the `cardiotrust` agent.
5. Show the `CardioTrust Demo` app reaching healthy status.
6. Open the app from the Coder dashboard, not from an unrelated local server.
7. Demonstrate a confident label, an uncertainty abstention, and an invalid
   input stop.
8. Show the locked holdout evidence and age-60-plus limitation.
9. Record the workspace/template version and the repository revision.

## Private model transfer

`artifacts/model.joblib` is intentionally excluded from version control because
trained-model publication has not been approved. A clean clone therefore
cannot run the demo until the exact locked artifact is transferred privately.

Expected artifact:

- bytes: `642767`
- SHA-256:
  `E2F42C05FDB8A48E088421A0C5D8FC60ED56C1DF9CF6C32FDE8277F1E09BF5CB`

The expected values are machine-readable in `artifacts/model_manifest.json`.
The startup script now refuses to launch when the file is absent, altered, or
when the Coder app has been changed from owner-only access.

## Evidence gap

The official Discord was joined read-only and no organizer was contacted. The
organizer requirement is now clear, but the promised challenge-specific guide
was not found. Therefore the repository is aligned with public Coder Dev
Container capabilities, while cash-prize compliance remains unproven until the
project is launched and recorded inside an eligible Coder workspace.

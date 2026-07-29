# Coder Demo Evidence Plan

Status date: 2026-07-29  
Status: organizer requirement confirmed; private local Coder execution and
authenticated demo recording complete; organizer acceptance still pending

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

## Demonstrated local deployment

On 2026-07-29 the project was also run in a real, self-hosted Coder v2.35.3
workspace:

- template: `Byte2Beat CardioTrust`
- workspace: `cardiotrust-demo`
- repository revision:
  `ab80188b28969d5dbb25598dbf38883b35b80dd9`
- private model hash and size: verified
- Coder preflight: PASS
- unit tests: 13 passed
- Streamlit health endpoint: `ok`
- port 8501: detected by Coder and kept owner-only

This concrete run used the Docker Containers template plus Git Clone rather
than the repository's Dev Container integration. Coder still provisioned and
managed the workspace and its application port. See
`docs/coder_local_deployment_2026-07-29.md`.

## Completed recording

`artifacts/recordings/coder_demo_final.mp4` is a 100-second authenticated
recording that shows:

1. the running `cardiotrust-demo` Coder workspace and ready agent
2. Coder detecting port 8501 as owner-only
3. the app opened through the Coder port proxy
4. an uncertainty abstention
5. an invalid-input stop
6. a high-confidence model signal
7. the locked holdout evidence and age-60-plus limitation

The private model hash, preflight PASS, 13 tests, health result, Coder version,
template, workspace, and repository revision remain recorded in the deployment
evidence note.

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

The initial official Discord review was read-only. On 2026-07-29 at 12:34 CEST,
a single clarification was sent in `#hackathon-discussion` asking whether the
authenticated local Coder recording is sufficient or a continuously online
public Coder URL is required. No attachment or local URL was sent. The response
is pending. Cash-prize compliance remains unproven until the organizers'
acceptance of a self-hosted, locally reachable deployment is known.

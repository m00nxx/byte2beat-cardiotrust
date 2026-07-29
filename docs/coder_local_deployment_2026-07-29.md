# Local Coder Deployment Evidence

Status date: 2026-07-29
Result: **PASS for a private local Coder execution; CONDITIONAL GO for cash
eligibility**

## Deployment

- Coder: `v2.35.3+65e2bfb`, self-hosted in Ubuntu on WSL2
- telemetry: disabled
- trial: not started
- template: `Byte2Beat CardioTrust`
- workspace: `cardiotrust-demo`
- workspace status: Running
- agent: `main`, Ready
- base image: `codercom/enterprise-base:ubuntu`
- repository revision:
  `ab80188b28969d5dbb25598dbf38883b35b80dd9`
- clone location: `/home/coder/byte2beat`

The template used Coder's Docker Containers base and the Git Clone module. The
repository was served from a native-WSL, local-only bare repository and was not
published to a remote Git host.

## Private model transfer

The trained model remained outside Git and was copied directly into the running
workspace container. Validation inside the workspace confirmed:

- path: `/home/coder/byte2beat/artifacts/model.joblib`
- bytes: `642767`
- SHA-256:
  `E2F42C05FDB8A48E088421A0C5D8FC60ED56C1DF9CF6C32FDE8277F1E09BF5CB`
- owner: `coder`
- mode: `0600`

No model bytes were shared publicly.

## Runtime validation

The workspace installed the exact versions in `requirements.txt` into
`.venv`. It then passed:

- `python scripts/coder_preflight.py`: `preflight: PASS`
- `python -m unittest discover -s tests -v`: 13 tests passed
- `curl http://127.0.0.1:8501/_stcore/health`: `ok`

The deployment runtime is Python 3.12.3. The validation-locked training
environment used Python 3.11.9. This is a documented runtime deviation, not a
claim of a byte-identical retraining environment. The locked model loaded and
all deployment tests passed without retraining.

## Coder access evidence

Coder detected the Streamlit listener on port 8501 and exposed it through the
workspace's authenticated, owner-only port proxy. An unauthenticated request to
the proxy received an authentication redirect and the Coder response identified
build `v2.35.3+65e2bfb`.

The dashboard evidence is:

- `artifacts/figures/coder_workspace_running.jpg`
- screenshot SHA-256:
  `D1B5ECAE23BA7A1E692D75ABFBC6053006321319B22D4C8794A449C53AF2CE00`

The image shows the running workspace, ready agent, and detected port 8501. No
port was shared with the organization or public.

The local control plane and Git source can be restarted in separate WSL
terminals with `scripts/start_local_coder_server.sh` and
`scripts/serve_local_repo.sh`. Both remain foreground processes deliberately;
this avoids relying on background WSL processes that may be terminated when
their launching session exits.

## Scope and limitations

This run demonstrates that the project executes inside an actual Coder-managed
workspace rather than only containing a Coder-compatible scaffold. It does not
yet establish organizer acceptance for the cash prize because:

- no challenge-specific Coder deployment guide was found
- the deployment is self-hosted and locally reachable
- no final demo video has been recorded
- no public endpoint has been created
- no organizer has reviewed or accepted this evidence

No publication, public sharing, organizer contact, or final Kaggle submission
was performed.

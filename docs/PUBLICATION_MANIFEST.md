# Public Submission Manifest

Publication date: 2026-07-29

## Included

- complete training, evaluation, inference, and Streamlit source code
- pinned Python dependencies and Dev Container/Coder configuration
- public Kaggle notebook source
- aggregate metrics, subgroup tables, validation folds, and figures
- validation lock, model card, provenance note, and technical report
- authenticated Coder demo recording and deployment evidence

## Excluded

- raw or transformed row-level datasets
- `artifacts/model.joblib`
- local runtime state, credentials, tokens, and session material
- unedited browser captures

The exclusions are enforced through `.gitignore`. Reviewers can download
`cardio_base.csv` from the official Byte2Beat resource folder and run:

```powershell
.\.venv\Scripts\python.exe -m src.run_experiment
```

This recreates the excluded model and all aggregate evaluation artifacts.

## Coder Evidence

`artifacts/recordings/coder_demo_final.mp4` shows the real self-hosted Coder
workspace, ready agent, owner-only port proxy, application behavior, and
documented limitations. The repository also includes the Dev Container
metadata and launch scripts used for the integration.

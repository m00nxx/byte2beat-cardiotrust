from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_preflight(root: Path = ROOT) -> list[str]:
    manifest_path = root / "artifacts" / "model_manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("Missing artifacts/model_manifest.json")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_path = root / manifest["file"]
    if not model_path.is_file():
        raise RuntimeError(
            "Missing artifacts/model.joblib. Transfer the locked private model "
            "artifact into the Coder workspace before starting the demo."
        )

    actual_bytes = model_path.stat().st_size
    if actual_bytes != manifest["bytes"]:
        raise RuntimeError(
            f"Model size mismatch: expected {manifest['bytes']}, got {actual_bytes}"
        )

    actual_sha256 = sha256_file(model_path)
    if actual_sha256 != manifest["sha256"]:
        raise RuntimeError(
            "Model SHA-256 mismatch: "
            f"expected {manifest['sha256']}, got {actual_sha256}"
        )

    required_evidence = (
        root / "artifacts" / "metrics.json",
        root / "artifacts" / "permutation_importance.csv",
    )
    missing_evidence = [str(path.relative_to(root)) for path in required_evidence if not path.is_file()]
    if missing_evidence:
        raise RuntimeError("Missing demo evidence: " + ", ".join(missing_evidence))

    devcontainer_path = root / ".devcontainer" / "devcontainer.json"
    config = json.loads(devcontainer_path.read_text(encoding="utf-8"))
    coder = config.get("customizations", {}).get("coder", {})
    apps = coder.get("apps", [])
    demo_apps = [app for app in apps if app.get("slug") == "cardiotrust-demo"]
    if len(demo_apps) != 1:
        raise RuntimeError("Expected exactly one Coder app with slug cardiotrust-demo")

    demo_app = demo_apps[0]
    if demo_app.get("share") != "owner":
        raise RuntimeError("Coder demo app must remain owner-only before publication approval")
    if demo_app.get("healthCheck", {}).get("url") != (
        "http://localhost:8501/_stcore/health"
    ):
        raise RuntimeError("Coder demo health check is missing or unexpected")

    return [
        f"model bytes: {actual_bytes}",
        f"model sha256: {actual_sha256}",
        "Coder app: cardiotrust-demo (owner-only)",
        "preflight: PASS",
    ]


def main() -> None:
    for line in validate_preflight():
        print(line)


if __name__ == "__main__":
    main()

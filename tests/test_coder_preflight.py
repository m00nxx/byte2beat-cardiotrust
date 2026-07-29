from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.coder_preflight import sha256_file, validate_preflight


class CoderPreflightTests(unittest.TestCase):
    def make_fixture(self, root: Path, model: bytes = b"locked-model") -> None:
        (root / "artifacts").mkdir()
        (root / ".devcontainer").mkdir()
        model_path = root / "artifacts" / "model.joblib"
        model_path.write_bytes(model)
        manifest = {
            "file": "artifacts/model.joblib",
            "bytes": len(model),
            "sha256": sha256_file(model_path),
        }
        (root / "artifacts" / "model_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (root / "artifacts" / "metrics.json").write_text("{}", encoding="utf-8")
        (root / "artifacts" / "permutation_importance.csv").write_text(
            "feature,importance\n", encoding="utf-8"
        )
        config = {
            "customizations": {
                "coder": {
                    "apps": [
                        {
                            "slug": "cardiotrust-demo",
                            "share": "owner",
                            "healthCheck": {
                                "url": "http://localhost:8501/_stcore/health"
                            },
                        }
                    ]
                }
            }
        }
        (root / ".devcontainer" / "devcontainer.json").write_text(
            json.dumps(config), encoding="utf-8"
        )

    def test_valid_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            self.assertEqual(validate_preflight(root)[-1], "preflight: PASS")

    def test_missing_model_stops_startup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            (root / "artifacts" / "model.joblib").unlink()
            with self.assertRaisesRegex(RuntimeError, "Transfer the locked private"):
                validate_preflight(root)

    def test_wrong_model_hash_stops_startup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            (root / "artifacts" / "model.joblib").write_bytes(b"tampered-data")
            with self.assertRaisesRegex(RuntimeError, "mismatch"):
                validate_preflight(root)

    def test_public_app_stops_startup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            config_path = root / ".devcontainer" / "devcontainer.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["customizations"]["coder"]["apps"][0]["share"] = "public"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "owner-only"):
                validate_preflight(root)


if __name__ == "__main__":
    unittest.main()

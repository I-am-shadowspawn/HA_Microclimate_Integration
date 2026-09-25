"""Distribution boundaries and deterministic archive regression tests."""

import hashlib
import json
import re
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import build_release


class ReleasePackageTests(unittest.TestCase):
    """Check the archive users install and the archive maintainers reproduce."""

    def test_distribution_is_reproducible_and_extractable(self) -> None:
        with TemporaryDirectory() as one, TemporaryDirectory() as two:
            first = build_release.build(Path(one))
            second = build_release.build(Path(two))
            assert [path.name for path in first] == [path.name for path in second]
            assert [(hashlib.sha256(path.read_bytes()).hexdigest()) for path in first] == [
                hashlib.sha256(path.read_bytes()).hexdigest() for path in second
            ]
            assert (Path(one) / "SHA256SUMS").read_bytes() == (
                Path(two) / "SHA256SUMS"
            ).read_bytes()
            for archive in first:
                with zipfile.ZipFile(archive) as bundle:
                    names = set(bundle.namelist())
                    assert bundle.testzip() is None
                    assert not any(
                        name.startswith((".matrix/", "results/", "dist/"))
                        or "/node_modules/" in name
                        or "/__pycache__/" in name
                        or "token.txt" in name
                        or "evo-captures/" in name
                        for name in names
                    )
                    for name in names:
                        if name.endswith((".md", ".json", ".txt")):
                            text = bundle.read(name).decode("utf-8")
                            assert not re.search(r"/(?:home/[^/]+|srv/dev)/", text), name
                            if name.startswith("fixtures/"):
                                assert not re.search(
                                    r'"(?:token|api_key|password|authorization)"\s*:', text, re.I
                                ), name
                    component = "custom_components/microclimate_integration/"
                    assert component + "brand/icon.png" in names
                    assert component + "LICENSE" in names
                    assert component + "frontend/microclimate-cards.js" in names
                    assert component + "frontend/THIRD_PARTY_NOTICES.txt" in names
                    assert component + "services.yaml" in names
                    with TemporaryDirectory() as extraction:
                        bundle.extractall(extraction)
                        manifest = json.loads(
                            (Path(extraction) / component / "manifest.json").read_text()
                        )
                        assert manifest["version"] == build_release.validate_metadata()
                        assert (
                            (Path(extraction) / component / "brand/icon.png")
                            .read_bytes()
                            .startswith(b"\x89PNG\r\n\x1a\n")
                        )
                        assert not (Path(extraction) / "node_modules").exists()
                    if "development" in archive.name:
                        assert {
                            "hacs.json",
                            "LICENSE",
                            "frontend/package-lock.json",
                            ".github/workflows/validate.yml",
                        } <= names
                        assert {
                            "fixtures/" + name for name in build_release.PUBLIC_FIXTURES
                        } <= names
                    else:
                        assert all(name.startswith(component) for name in names)

    def test_unreviewed_fixture_is_not_packaged(self) -> None:
        path = build_release.ROOT / "fixtures" / "private-unreviewed-capture.json"
        try:
            path.write_text('{"token":"private"}')
            with TemporaryDirectory() as directory:
                development = build_release.build(Path(directory))[1]
                with zipfile.ZipFile(development) as bundle:
                    assert "fixtures/private-unreviewed-capture.json" not in bundle.namelist()
        finally:
            path.unlink(missing_ok=True)

    def test_credentials_and_hidden_metadata_are_not_packaged(self) -> None:
        candidates = [
            build_release.ROOT / "frontend" / "device-token.txt",
            build_release.ROOT / "frontend" / ".unreviewed-sensitive.json",
        ]
        assert all(not path.exists() for path in candidates)
        try:
            for path in candidates:
                path.write_text("private")
            with TemporaryDirectory() as directory:
                development = build_release.build(Path(directory))[1]
                with zipfile.ZipFile(development) as bundle:
                    names = set(bundle.namelist())
                    assert not any(
                        str(path.relative_to(build_release.ROOT)) in names for path in candidates
                    )
        finally:
            for path in candidates:
                path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

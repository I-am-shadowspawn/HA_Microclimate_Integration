#!/usr/bin/env python3
"""Build reproducible manual-install and development archives without deploying."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "microclimate_integration"
MINIMUM_HA = "2026.9.3"
COMPONENT = Path("custom_components") / DOMAIN

# Add public fixtures here only after sanitization and review.
PUBLIC_FIXTURES = (
    "captured_controller_2.json",
    "captured_evo_connect.json",
    "captures_20260923.json",
    "compact-day-night-evo-ii.json",
    "mapping_confirmation.json",
    "schedule_contract.json",
    "synthetic_get_all.json",
    "temperature_contract.json",
    "write_captures.json",
)
DEVELOPMENT_DIRECTORIES = (
    "tests",
    "harness_tests",
    "requirements",
    "scripts",
    "docs",
    "frontend",
    ".github",
)
DEVELOPMENT_ROOT_FILES = (
    ".gitignore",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "PIN-VERIFICATION.md",
    "README.md",
    "README-TESTING.md",
    "SECURITY.md",
    "SUPPORT.md",
    "TODO.md",
    "conftest.py",
    "hacs.json",
    "pytest-review.ini",
    "ruff.toml",
)
PUBLIC_SUFFIXES = {
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".png",
    ".py",
    ".txt",
    ".ts",
    ".yaml",
    ".yml",
    ".toml",
}
PUBLIC_NAMES = {"LICENSE", "CODEOWNERS", ".gitignore"}
SENSITIVE_NAMES = {
    "device-token.txt",
    "token.txt",
    "secrets.json",
    "credentials.json",
}
EXCLUDED_PARTS = {
    ".git",
    ".matrix",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "playwright-report",
    "results",
    "test-results",
}


def public_file(path: Path) -> bool:
    """Accept reviewable source/metadata; never include caches or symlinks."""
    relative = path.relative_to(ROOT)
    if path.is_symlink() or not path.is_file():
        return False
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if any(part.startswith(".") and part != ".github" for part in relative.parts[:-1]):
        return False
    if path.name.startswith(".") and path.name != ".gitignore":
        return False
    if path.name.lower() in SENSITIVE_NAMES:
        return False
    return path.suffix in PUBLIC_SUFFIXES or path.name in PUBLIC_NAMES


def files_under(directory: Path) -> list[Path]:
    """Collect files from an explicitly named public source directory."""
    return sorted(path for path in (ROOT / directory).rglob("*") if public_file(path))


def require_paths(paths: list[Path]) -> None:
    """Fail closed if a required release input disappears or becomes a link."""
    for path in paths:
        if not public_file(path):
            raise ValueError(f"Missing or unsafe release input: {path.relative_to(ROOT)}")


def validate_metadata() -> str:
    """Ensure the distributable and its build inputs describe one version."""
    manifest = json.loads((ROOT / COMPONENT / "manifest.json").read_text())
    hacs = json.loads((ROOT / "hacs.json").read_text())
    frontend = json.loads((ROOT / "frontend/package.json").read_text())
    lockfile = json.loads((ROOT / "frontend/package-lock.json").read_text())
    if manifest.get("domain") != DOMAIN or manifest.get("config_flow") is not True:
        raise ValueError("Invalid integration manifest domain or config flow")
    if manifest.get("requirements") != [] or not manifest.get("codeowners"):
        raise ValueError("Unexpected runtime requirements or missing codeowner")
    version = manifest.get("version")
    if not isinstance(version, str) or any(
        candidate != version
        for candidate in (
            frontend.get("version"),
            lockfile.get("version"),
            lockfile.get("packages", {}).get("", {}).get("version"),
        )
    ):
        raise ValueError("Manifest, frontend package and lockfile versions differ")
    if hacs.get("homeassistant") != MINIMUM_HA:
        raise ValueError(f"HACS minimum must be Core {MINIMUM_HA}")
    return version


def archive(path: Path, files: list[Path]) -> None:
    """Write fixed-order ZIP entries with stable timestamps and permissions."""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for source in sorted(set(files)):
            relative = source.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, source.read_bytes())
        if bundle.testzip() is not None:
            raise ValueError(f"Archive integrity check failed: {path}")


def build(output: Path) -> list[Path]:
    """Create config-root install ZIP and complete development ZIP."""
    version = validate_metadata()
    required_component = [
        ROOT / COMPONENT / name
        for name in (
            "__init__.py",
            "manifest.json",
            "LICENSE",
            "brand/icon.png",
            "frontend/microclimate-cards.js",
            "frontend/THIRD_PARTY_NOTICES.txt",
        )
    ]
    require_paths(required_component)
    component = files_under(COMPONENT)
    for source in component:
        if source.suffix == ".py":
            compile(source.read_text(), str(source), "exec")

    required_development = [ROOT / name for name in DEVELOPMENT_ROOT_FILES]
    required_development += [ROOT / "fixtures" / name for name in PUBLIC_FIXTURES]
    require_paths(required_development)
    development = component + required_development
    for directory in DEVELOPMENT_DIRECTORIES:
        development.extend(files_under(Path(directory)))

    output.mkdir(parents=True, exist_ok=True)
    checksums = []
    archives = []
    for kind, files in (("install", component), ("development", development)):
        destination = output / f"microclimate-{version}-{kind}.zip"
        archive(destination, files)
        checksums.append(
            f"{hashlib.sha256(destination.read_bytes()).hexdigest()}  {destination.name}\n"
        )
        archives.append(destination)
    (output / "SHA256SUMS").write_text("".join(checksums))
    return archives


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    archives = build(args.output)
    for archive_path in archives:
        print(f"Built {archive_path}")
    print((args.output / "SHA256SUMS").read_text(), end="")


if __name__ == "__main__":
    main()

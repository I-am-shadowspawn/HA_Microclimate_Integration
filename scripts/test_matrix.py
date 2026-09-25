#!/usr/bin/env python3
"""Reproduce pinned HA/Python test environments without running an HA server."""

import argparse
import json
import os
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = [("2026.9.3", "0.13.366")]
# The 2026.9.2 lockfile remains historical test evidence below the supported minimum.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--install",
        action="store_true",
        help="Create/synchronize isolated venvs from pinned requirements",
    )
    parser.add_argument(
        "--release-gate",
        action="store_true",
        help="Run known-defect tests normally; any remaining defect fails",
    )
    parser.add_argument("--ha", choices=[row[0] for row in MATRIX], help="Run only one matrix row")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 14):
        parser.error("Home Assistant 2026.9.3 tests require Python 3.14.x")
    env = os.environ.copy()
    results = []
    for ha, plugin in MATRIX:
        if args.ha and args.ha != ha:
            continue
        target = ROOT / ".matrix" / f"ha-{ha}"
        output = ROOT / "results" / "matrix" / f"ha-{ha}"
        output.mkdir(parents=True, exist_ok=True)
        python = target / "bin" / "python"
        if args.install:
            if not python.exists():
                subprocess.run(
                    ["uv", "venv", "--python", sys.executable, str(target)],
                    check=True,
                    cwd=ROOT,
                    env=env,
                )
            with (output / "install.log").open("w") as log:
                subprocess.run(
                    [
                        "uv",
                        "--native-tls",
                        "pip",
                        "sync",
                        "--python",
                        str(python),
                        str(ROOT / "requirements" / f"ha-{ha}.txt"),
                    ],
                    check=True,
                    cwd=ROOT,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
        if not python.exists():
            parser.error("Matrix environment missing; use --install")
        with (output / "dependency-check.log").open("w") as log:
            subprocess.run(
                ["uv", "pip", "check", "--python", str(python)],
                check=True,
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        probe = 'import json,platform; from importlib.metadata import version; print(json.dumps({"python":platform.python_version(),"homeassistant":version("homeassistant"),"plugin":version("pytest-homeassistant-custom-component")}))'
        metadata = json.loads(
            subprocess.check_output([str(python), "-c", probe], text=True, cwd=ROOT)
        )
        assert metadata == {
            "python": platform.python_version(),
            "homeassistant": ha,
            "plugin": plugin,
        }, metadata
        (output / "versions.json").write_text(json.dumps(metadata, indent=2) + "\n")
        suffix = "release" if args.release_gate else "regression"
        command = [
            str(python),
            "-m",
            "pytest",
            "-c",
            "pytest-review.ini",
            "tests",
            "harness_tests",
            "-q",
            f"--junitxml={output}/{suffix}.xml",
            "--cov=custom_components.microclimate_integration",
            f"--cov-report=xml:{output}/{suffix}-coverage.xml",
            "--cov-report=term",
        ]
        if args.release_gate:
            command += ["--runxfail"]
        print(f"Running HA {ha}, Python {platform.python_version()} ({suffix})", flush=True)
        run_env = {**env, "COVERAGE_FILE": str(output / ".coverage")}
        with (output / f"{suffix}.log").open("w") as log:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                env=run_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in process.stdout:
                log.write(line)
                print(line, end="", flush=True)
            code = process.wait()
        suite = ET.parse(output / f"{suffix}.xml").getroot().find("testsuite")
        results.append(
            {
                **metadata,
                "exit_code": code,
                "counts": dict(suite.attrib),
                "log": str(output / f"{suffix}.log"),
            }
        )
    summary = (
        ROOT
        / "results"
        / "matrix"
        / f"{args.ha or 'all'}-{'release' if args.release_gate else 'regression'}-summary.json"
    )
    summary.write_text(json.dumps(results, indent=2) + "\n")
    return int(any(result["exit_code"] for result in results))


if __name__ == "__main__":
    sys.exit(main())

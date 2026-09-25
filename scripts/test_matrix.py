#!/usr/bin/env python3
"""Reproduce pinned HA/Python test environments without running an HA server."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MATRIX = [('2026.9.2', '0.13.365'), ('2026.9.3', '0.13.366')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Create/synchronize isolated venvs from pinned requirements')
    parser.add_argument('--release-gate', action='store_true', help='Run known-defect tests normally; any remaining defect fails')
    parser.add_argument('--ha', choices=[row[0] for row in MATRIX], help='Run only one matrix row')
    args = parser.parse_args()
    if platform.python_version() != '3.14.7':
        parser.error('This matrix is pinned to Python 3.14.7; run with that interpreter')
    env = {**os.environ, 'UV_CACHE_DIR': str(ROOT.parent/'uv-cache')}
    results = []
    for ha, plugin in MATRIX:
        if args.ha and args.ha != ha:
            continue
        target = ROOT/'.matrix'/f'ha-{ha}'
        output = ROOT/'results'/'matrix'/f'ha-{ha}'
        output.mkdir(parents=True,exist_ok=True)
        python = target/'bin'/'python'
        if args.install:
            subprocess.run(['uv','venv','--python',sys.executable,str(target)],check=True,cwd=ROOT,env=env) if not python.exists() else None
            with (output/'install.log').open('w') as log:
                subprocess.run(['uv','--native-tls','pip','sync','--python',str(python),str(ROOT/'requirements'/f'ha-{ha}.txt')],check=True,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        if not python.exists():
            parser.error('Matrix environment missing; use --install')
        with (output/'dependency-check.log').open('w') as log:
            subprocess.run(['uv','pip','check','--python',str(python)],check=True,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        probe = 'import json,platform; from importlib.metadata import version; print(json.dumps({"python":platform.python_version(),"homeassistant":version("homeassistant"),"plugin":version("pytest-homeassistant-custom-component")}))'
        metadata=json.loads(subprocess.check_output([str(python),'-c',probe],text=True,cwd=ROOT))
        assert metadata == {'python':'3.14.7','homeassistant':ha,'plugin':plugin}, metadata
        (output/'versions.json').write_text(json.dumps(metadata,indent=2)+'\n')
        suffix = 'release' if args.release_gate else 'regression'
        command=[str(python),'-m','pytest','-c','pytest-review.ini','tests','harness_tests','-q',f'--junitxml={output}/{suffix}.xml','--cov=custom_components.microclimate_integration',f'--cov-report=xml:{output}/{suffix}-coverage.xml','--cov-report=term']
        if args.release_gate:
            command += ['--runxfail']
        print(f'Running HA {ha}, Python 3.14.7 ({suffix})',flush=True)
        run_env = {**env, 'COVERAGE_FILE':str(output/'.coverage')}
        with (output/f'{suffix}.log').open('w') as log:
            process = subprocess.Popen(command,cwd=ROOT,env=run_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            for line in process.stdout:
                log.write(line)
                print(line,end='',flush=True)
            code=process.wait()
        suite = ET.parse(output/f'{suffix}.xml').getroot().find('testsuite')
        results.append({**metadata,'exit_code':code,'counts':dict(suite.attrib),'log':str(output/f'{suffix}.log')})
    summary=ROOT/'results'/'matrix'/f'{args.ha or "all"}-{"release" if args.release_gate else "regression"}-summary.json'
    summary.write_text(json.dumps(results,indent=2)+'\n')
    return int(any(result['exit_code'] for result in results))


if __name__ == '__main__':
    sys.exit(main())

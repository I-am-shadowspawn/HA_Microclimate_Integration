#!/usr/bin/env python3
"""Build reproducible manual-install and development archives, without deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'microclimate_integration'


def files_under(directory):
    allowed_suffixes = {'.py', '.json', '.txt', '.md', '.ini', '.js', '.mjs',
                        '.ts', '.css', '.html', '.png', '.yaml', '.yml'}
    selected = []
    for path in (ROOT / directory).rglob('*'):
        if not path.is_file():
            continue
        parts = path.relative_to(ROOT).parts
        if any((part.startswith('.') and part != '.github') or
               part in ('__pycache__', 'node_modules', 'test-results', 'playwright-report')
               for part in parts):
            continue
        if path.suffix in allowed_suffixes or path.name in {'LICENSE', 'CODEOWNERS'}:
            selected.append(path)
    return selected


def archive(path, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for source in sorted(set(files)):
            info = zipfile.ZipInfo(source.relative_to(ROOT).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, source.read_bytes())
        if bundle.testzip() is not None:
            raise RuntimeError('Archive verification failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    component = files_under('custom_components/' + DOMAIN)
    manifest = json.loads((ROOT / 'custom_components' / DOMAIN / 'manifest.json').read_text())
    assert manifest['domain'] == DOMAIN and manifest['config_flow'] is True
    assert manifest['requirements'] == [] and '@your_github_username' not in manifest['codeowners']
    for path in component:
        if path.suffix == '.py':
            compile(path.read_text(), str(path), 'exec')
    development = list(component)
    for directory in ('tests', 'harness_tests', 'fixtures', 'requirements', 'scripts', 'docs', 'frontend', '.github'):
        development.extend(files_under(directory))
    development.extend(ROOT / name for name in ('README.md', 'TODO.md', 'CHANGELOG.md', 'README-TESTING.md',
                                               'PIN-VERIFICATION.md', 'conftest.py', 'pytest-review.ini', 'LICENSE', 'hacs.json',
                                               'CONTRIBUTING.md', 'SUPPORT.md', 'SECURITY.md', '.gitignore'))
    args.output.mkdir(parents=True, exist_ok=True)
    sums = []
    for kind, files in (('install', component), ('development', development)):
        destination = args.output / f"microclimate-{manifest['version']}-{kind}.zip"
        archive(destination, files)
        sums.append(f'{hashlib.sha256(destination.read_bytes()).hexdigest()}  {destination.name}\n')
    (args.output / 'SHA256SUMS').write_text(''.join(sums))
    print(''.join(sums), end='')


if __name__ == '__main__':
    main()

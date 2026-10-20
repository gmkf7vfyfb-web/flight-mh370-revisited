#!/usr/bin/env python3
"""Verify the immutable capsule ledger and retained broad-run identities."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    checked = 0
    for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
        expected, relative = line.split('  ', 1)
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT), relative
        assert path.is_file() and not path.is_symlink(), relative
        assert digest(path) == expected, relative
        checked += 1
    binary = digest(ROOT / 'bin/linux-x86_64/mh370-v0.1')
    for flight, name in [('mh371', 'broad-flight-truth-control'),
                         ('mh370', 'broad-flight-uncertainty-diagnostic')]:
        run = ROOT / 'workspace/runs' / flight / name
        manifest = json.loads((run / 'run-manifest.json').read_text())
        summary = json.loads((run / 'summary.json').read_text())
        report_path = run / 'diagnostic-report/broad_snapshot_diagnostic.json'
        report = json.loads(report_path.read_text())
        validation = json.loads((run / 'diagnostic-report/release-validation.json').read_text())
        assert manifest['command'] == 'estimate-broad-flight'
        assert summary['model_family'] == 'broad-powered-marked-jump-v1'
        assert manifest['executable_sha256'] == binary
        assert validation['status'] == 'passed'
        assert all(c['status'] == 'passed' for c in validation['checks'])
        assert validation['identities']['report_audit_sha256'] == digest(report_path)
        assert report['numerical_support']['status'] == 'failed'
        assert report['numerical_support']['publication_eligible'] is False
        print(f'{flight}: provenance passed; numerical support FAILED; diagnostic only')
    print(f'Verified {checked} files. No scientific convergence claim follows.')

if __name__ == '__main__':
    main()

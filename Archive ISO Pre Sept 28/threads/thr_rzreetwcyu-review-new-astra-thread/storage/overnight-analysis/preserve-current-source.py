"""Preserve the current analysis code without copying large caches or papers."""

import datetime as dt
import gzip
import hashlib
import importlib.metadata
import io
import json
import pathlib
import subprocess
import tarfile


ROOT = pathlib.Path('/jackbox/home/MH370')
OUTPUT = pathlib.Path(__file__).resolve().parent
PROTOTYPE = pathlib.Path('/tmp/mh370-command-sampler')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def source_files():
    files = {}
    for name in ['AGENTS.md', 'Cargo.toml', 'Cargo.lock', 'README.md',
                 'rust-toolchain.toml', '.gitignore']:
        files['project/' + name] = ROOT / name
    for folder in ['crates', 'configs', 'inputs']:
        for path in (ROOT / folder).rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if folder == 'inputs' and path.suffix == '.bin' and path.stat().st_size > 1_000_000:
                continue
            files['project/' + str(path.relative_to(ROOT))] = path
    packages = {
        'holland-2018-bfo-descent': ['README.md', 'code/recreate.py',
                                  'data/observations-and-conditions.json'],
        'kadri-2024-hydroacoustics': ['README.md', 'code/preferred_event_geometry.py',
                                    'data/conditional-geometry-config.json', 'data/citation-ledger.md'],
        'godfrey-wspr-passive-radar': ['README.md', 'citation-ledger.md',
                                     'code/audit_proposed_trajectory.py',
                                     'data/proposed-trajectory-2023.csv',
                                     'data/terminal-hypotheses-2023.json'],
        'mh370-seabed-search-coverage': ['README.md', 'data/current-contract-status.json'],
    }
    for package, names in packages.items():
        for name in names:
            path = ROOT / '.sources' / package / name
            files['project/' + str(path.relative_to(ROOT))] = path
    for path in PROTOTYPE.iterdir():
        if path.is_file() and path.suffix in ['.py', '.md']:
            files['research-not-integrated/command-sampler/' + path.name] = path
    files['preserve-current-source.py'] = pathlib.Path(__file__)
    assert all(path.is_file() for path in files.values())
    return files


def main():
    files = source_files()
    included = {path.resolve() for path in files.values()}
    external = []
    for path in sorted((ROOT / 'inputs').rglob('*')):
        if path.is_file() and path.resolve() not in included:
            external.append({'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)})
    binary = ROOT / 'target/release/mh370'
    manifest = {
        'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'purpose': 'Current code preservation; not a complete data deposit or all historical revisions',
        'git_revision': None,
        'git_revision_reason': 'No Git metadata is present in this workspace.',
        'included': {name: {'source_path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)}
                     for name, path in sorted(files.items())},
        'external_input_files': external,
        'runner_binary': {'path': str(binary), 'bytes': binary.stat().st_size, 'sha256': digest(binary)},
        'rustc': subprocess.check_output(['rustc', '--version'], text=True).strip(),
        'python': subprocess.check_output(['python', '--version'], text=True).strip(),
        'numerical_python_packages': {name: importlib.metadata.version(name)
                                      for name in ['numpy', 'scipy', 'matplotlib']},
        'limitations': [
            'Large environmental grids remain at their recorded paths and are not copied.',
            'Saved run artifacts remain in the pre-analysis and overnight-analysis directories.',
            'Paper PDFs are not bundled; source READMEs record citations and available hashes.',
            'The rejected sampling prototype is outside the product and must not be treated as a validated estimator.',
            'Missing earlier prototype and runner revisions cannot be reconstructed by this snapshot.',
            'Some paths in configurations and manifests remain host-specific.',
        ],
    }
    archive = OUTPUT / 'source-snapshot.tar.gz'
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as tar:
                for name, path in sorted(files.items()):
                    info = tar.gettarinfo(str(path), arcname=name)
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ''
                    with path.open('rb') as stream:
                        tar.addfile(info, stream)
                body = json.dumps(manifest, indent=2).encode()
                info = tarfile.TarInfo('snapshot-manifest.json')
                info.size = len(body)
                tar.addfile(info, io.BytesIO(body))
    manifest['archive'] = {'name': archive.name, 'bytes': archive.stat().st_size, 'sha256': digest(archive)}
    (OUTPUT / 'source-snapshot.json').write_text(json.dumps(manifest, indent=2))
    for name in [archive.name, 'source-snapshot.json']:
        link = OUTPUT / 'web' / name
        if not link.exists():
            link.symlink_to(pathlib.Path('..') / name)
    with tarfile.open(archive) as tar:
        for name, record in manifest['included'].items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == record['sha256'], name
    print(json.dumps({'preserved_files': len(files), 'archive': manifest['archive'],
                      'external_inputs': len(external), 'verified_archive_members': len(files)}))


if __name__ == '__main__':
    main()

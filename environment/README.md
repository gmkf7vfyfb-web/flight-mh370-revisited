# Runtime environment

The migration runtime was Python 3.12.13 and Node.js 24.14.0. Install the core
Python environment with:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r environment/requirements-lock.txt
```

Core estimator code is Python. Most `.mjs` files use Node built-ins for workbook
handling, but `inspect_logs.mjs` and `inspect_mh370_workbooks.mjs` depend on the
harness-specific `@oai/artifact-tool` and are not portable without an
equivalent environment.

Run the lightweight handoff validation with:

```bash
python scripts/migration/verify_handoff.py
```

Particle-filter reruns are computationally expensive and should follow a
successful lightweight validation. New production runs should create a new
environment lock or container digest and record it in the run manifest.


# Project registry and checks. Use: make -C "Claude Science Project Sep 29/registry" <target>
PY ?= python3
MEMORIES ?= memories_export.json

.PHONY: check report registry backfill build index baseline baseline-modules install-hooks
check:          ## rules for new work (C1-C4); fails on a new violation only
	$(PY) check_project.py
report:         ## list every existing violation (not fixed) in existing_violations.tsv
	$(PY) check_project.py --report-existing existing_violations.tsv
backfill:       ## generate modules/*/entries.yaml from records (needs a memory export JSON)
	$(PY) backfill_registry.py --memories "$(MEMORIES)"
build:          ## hash, manifests, module REGISTRY.json files and the merged REGISTRY.json
	$(PY) build_registry.py
index:          ## results/INDEX.md and COVERAGE.md from REGISTRY.json
	$(PY) make_index.py
registry: backfill build index
baseline:       ## only at a registry rebuild: record the tracked paths that count as old
	$(PY) check_project.py --make-baseline
baseline-modules: ## at a registry build: freeze the paths and known C4 keys of each module branch (remote heads)
	$(PY) check_project.py --make-module-baseline
install-hooks:  ## install the pre-push check in this clone
	sh install_hooks.sh

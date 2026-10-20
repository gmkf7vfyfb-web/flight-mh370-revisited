# Local app (macOS):     make app                      then open the bundle it writes
# Local app (here):      make serve
# Base estimate:         make report
# One hypothesis:        make hypothesis H=<name>      (full run, compared with the base)
# Quick code check:      make smoke [H=<name>]         (~1 min; never for conclusions)
# Core sensitivity:      make sensitivity S=<name>     (config/sensitivity/<name>.toml over the base)
# New hypothesis:        make new-hypothesis H=<name>
# Hypothesis scope:      make scope H=<name>           (fails if the branch touches anything else)
# Core refactor check:   make regress [REF=<commit>]   (base output byte-identical to REF, default main)
# Impact fixture:        make fixture                  (runs/fixture: smoke scale, 00:11 stop, placeholder impacts)
# Impact module check:   make evaluate H=<name>        (that module on the fixture's impacts, in seconds)
PYTHON ?= .venv/bin/python
CONFIG ?= config/davey2016.toml
RUN    ?= runs/davey2016

.PHONY: report run app serve hypothesis sensitivity control smoke fixture evaluate new-hypothesis scope regress test venv clean need-H need-base

report: $(RUN)/run.json
	$(PYTHON) report/build_report.py $(RUN) mh370-davey2016-reproduction.pdf

$(RUN)/run.json: $(CONFIG)
	cargo run --release -- $(CONFIG) $(RUN)

run:
	cargo run --release -- $(CONFIG) $(RUN)

# The app runs the same filter as `make run`, in a window. Its runs go to runs/<name>
# and can be repeated from the command line with the override it shows.
serve:
	cargo run --release -- serve

APP := MH370 Particle Filter.app
app:
	cargo build --release
	rm -rf "$(APP)"
	mkdir -p "$(APP)/Contents/MacOS"
	cp target/release/mh370 "$(APP)/Contents/MacOS/mh370"
	printf '#!/bin/sh\nexec "$$(dirname "$$0")/mh370" serve --root "%s"\n' '$(CURDIR)' > "$(APP)/Contents/MacOS/app"
	chmod +x "$(APP)/Contents/MacOS/app"
	printf '%s\n' "$$PLIST" > "$(APP)/Contents/Info.plist"
	@echo 'Built "$(APP)": double-click it, or run: open "$(APP)"'

define PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>MH370 Particle Filter</string>
<key>CFBundleDisplayName</key><string>MH370 Particle Filter</string>
<key>CFBundleIdentifier</key><string>org.mh370.particle-filter</string>
<key>CFBundleExecutable</key><string>app</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleVersion</key><string>1.0.0</string>
<key>CFBundleShortVersionString</key><string>1.0.0</string>
<key>LSMinimumSystemVersion</key><string>11.0</string>
</dict></plist>
endef
export PLIST

hypothesis: need-H need-base
	cargo test --release -p mh370-hypotheses
	cargo run --release -- hypotheses/$(H)/run.toml runs/$(H)
	$(PYTHON) report/build_report.py runs/$(H) runs/$(H)/report.pdf --baseline $(RUN)

sensitivity: need-base
	@test -n "$(S)" || { echo "usage: make sensitivity S=<name>"; exit 1; }
	cargo run --release -- $(CONFIG) config/sensitivity/$(S).toml runs/$(S)
	$(PYTHON) report/build_report.py runs/$(S) runs/$(S)/report.pdf --baseline $(RUN)

# Known-flight control (MH371), blind: config/control/mh371.toml and the scorer were committed
# before the first run; only report/mh371_score.py reads the ACARS truth.
ACARS ?= /jackbox/home/MH370-inputs/acars/mh370-acars-position-and-wind-reports.xlsx
# Replicates run one at a time; each is reduced to its truth-free arc summary and its particle
# arrays are deleted before the next (peak disk ~0.7 GB). Run under the heavy-job lock.
control:
	mkdir -p runs/mh371
	for s in 1 2 3 4; do \
	  printf 'seeds = [%s]\n' $$s > runs/mh371/seed.toml && \
	  cargo run --release -- $(CONFIG) config/control/mh371.toml runs/mh371/seed.toml runs/mh371 && \
	  $(PYTHON) report/mh371_score.py summarise runs/mh371 $$s && \
	  rm -f runs/mh371/bto-only/seed-$$s/final.npy || exit 1; done
	$(PYTHON) report/mh371_score.py score runs/mh371 $(ACARS)

SMOKE := runs/smoke-$(or $(H),base)
smoke:
	cargo run --release -- $(if $(H),hypotheses/$(H)/run.toml,$(CONFIG)) config/smoke.toml $(SMOKE)
	$(PYTHON) report/build_report.py $(SMOKE) $(SMOKE)/report.pdf

# Impact modules test against a small cached run instead of a full one. It is rebuilt when its
# configs change; delete runs/fixture to rebuild it after a code change.
FIXTURE := runs/fixture
FIXTURE_CONFIGS := config/integrated.toml config/smoke.toml config/fixture.toml
fixture: $(FIXTURE)/run.json

$(FIXTURE)/run.json: $(FIXTURE_CONFIGS)
	rm -rf $(FIXTURE)
	cargo run --release -- $(FIXTURE_CONFIGS) $(FIXTURE)

evaluate: need-H $(FIXTURE)/run.json
	cargo run --release -- evaluate hypotheses/$(H)/run.toml $(FIXTURE)/bto-bfo/seed-1/impacts.npy runs/evaluate-$(H)

new-hypothesis: need-H
	@test ! -e hypotheses/$(H) || { echo "hypotheses/$(H) already exists"; exit 1; }
	cp -r hypotheses/_template hypotheses/$(H)
	sed -i 's/template/$(H)/g' hypotheses/$(H)/run.toml hypotheses/$(H)/lib.rs
	@echo "Created hypotheses/$(H)/. Work only there; check with: make scope H=$(H)"

scope: need-H
	@changed="$$( { git diff --name-only main...HEAD; git diff --name-only HEAD; \
	                git ls-files --others --exclude-standard; } | sort -u | grep -v '^$$' )"; \
	outside="$$(printf '%s\n' "$$changed" | grep -v '^hypotheses/$(H)/' || true)"; \
	if [ -n "$$outside" ]; then printf 'Out of scope for hypothesis $(H):\n%s\n' "$$outside"; exit 1; fi; \
	echo "In scope: every change is under hypotheses/$(H)/"

# One scratch directory per worktree (a hash of its path), so that regressions in different
# worktrees cannot delete each other; `:=`, so no environment variable can steer the rm -rf.
# The particle arrays it compares are float32, so differences below single precision pass.
REGRESS := /tmp/mh370-regress-$(shell printf '%s' '$(CURDIR)' | cksum | cut -d' ' -f1)
REF     ?= main
# Each side runs its own base configuration, so a changed input or prior is caught too.
# The reference tree borrows this one's environment grids, which git does not carry.
regress:
	rm -rf $(REGRESS) && git worktree prune
	git worktree add --detach $(REGRESS)/main $(REF)
	ln -s $(CURDIR)/data/*.bin $(REGRESS)/main/data/
	CARGO_TARGET_DIR=$(REGRESS)/target cargo build --release --manifest-path $(REGRESS)/main/Cargo.toml
	cargo build --release
	cd $(REGRESS)/main && $(REGRESS)/target/release/mh370 $(CONFIG) $(CURDIR)/config/smoke.toml $(REGRESS)/out-main
	target/release/mh370 $(CONFIG) config/smoke.toml $(REGRESS)/out-branch
	@for f in $$(cd $(REGRESS)/out-main && find . -name '*.npy' | sort); do \
	  cmp -s $(REGRESS)/out-main/$$f $(REGRESS)/out-branch/$$f || { echo "DIFFERS: $$f"; exit 1; }; done
	git worktree remove --force $(REGRESS)/main
	@echo "Base estimate is byte-identical to $(REF)."

test:
	cargo test --release

venv:
	python3 -m venv .venv && .venv/bin/pip install numpy matplotlib openpyxl xarray zarr gcsfs

clean:
	rm -rf runs target

# Comparisons need a base run but never rebuild it (it takes ~90 minutes).
need-base:
	@test -f $(RUN)/run.json || { echo "no base run in $(RUN): run 'make report' first"; exit 1; }

need-H:
	@test -n "$(H)" || { echo "usage: make $(firstword $(MAKECMDGOALS)) H=<hypothesis-name>"; exit 1; }

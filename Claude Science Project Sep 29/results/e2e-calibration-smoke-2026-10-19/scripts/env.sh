# sourced by every e2e script on deskstar
E2E=$HOME/mh370/e2e; ENG="$E2E/src/Claude Science Project Sep 29/engine"; BIN=$E2E/mh370-e2e; PY=$E2E/venv/bin/python
S=config/sensitivity; X=$S/fuel-fixes; F=$S/early-families; RJ=$S/run-j; H=hypotheses/end-of-flight
COMMON="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml"
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml"
CHAIN_WP="$COMMON $CX $F/speed-envelope-throughout.toml $S/handoff-lookahead-d.toml $RJ/obs-bfo432.toml $RJ/kx.toml $F/route-sampler.toml $RJ/size-sampler.toml"
EOF_A="$H/smoke/snapshot-m0011.toml $H/smoke/terminal.toml $H/full/reference-289.toml $H/full/descent-idle-floor.toml"
EOF_EXTRA="$H/smoke/v2-broad.toml $H/full/family-b-ditching.toml $H/full/residual-bank-boeing.toml $H/smoke/trim-at-loss.toml $H/full/pushover.toml $H/full/boeing-sequence.toml $H/full/b-late-onset-proposal.toml $H/full/holland-estimable.toml $H/full/a1-aimed-pitchdown.toml $H/full/piloted-turns.toml $H/full/run-i.toml $H/smoke/within-parent-unnormalised.toml"
EOF_RJ="$H/full/c2-silent-aim.toml $H/full/dive-branch.toml $H/smoke/children-16.toml $H/full/round3-laws.toml $H/full/bank-cap-uniform.toml"
export PYTHONPATH=$E2E/py:"$ENG/$H/smoke"
tl() { echo "$(date -u +%FT%TZ) $*" | tee -a $E2E/timeline.txt; }

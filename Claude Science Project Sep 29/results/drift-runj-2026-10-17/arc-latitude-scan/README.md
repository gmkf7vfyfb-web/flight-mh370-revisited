# Arc-latitude drift scan (dedicated run), queued 17 Oct 2026 18:27Z on deskstar

Pete's GO ~18:15Z. 66 release points: 0.5 deg steps 33-40 S at 1e6 particles (particles_per_class 83334 x 3 classes x 4 env),
1 deg steps 26-32 S at 3e5 (25000); each latitude at the run J D0 median impact longitude and +/-50 NM perpendicular
(arclat-release-points.csv; nodes on a 5 NM source grid, snapped within 3.3 NM of target).
Configs = aus160-<model>.toml unchanged except spacing_nm 5, node_subset, particles_per_class, output_dir, and one added
level alternative 'populated' (city+inner regional ln 1, all other Australian coast off). Pre-registered B (base ln_l) and C,
off, A, searcher are emitted as before. Order: GlobCurrent south, north, GLORYS12 south, north (chain_arclat.sh, waits for the
drift thread's chain3, then takes the heavy lock without timeout). Smoke (3 nodes, 100 ppc) passed: positions match, all
level columns present. Outputs: ~/mh370/drift/runs/arclat-<model>-<band>/nodes.csv, copied to ~/mh370/drift/arclat/.
Expected cost about 42 s per node per 1e5 particles (aus160 pilot): about 6 h per model, about 12 h total.

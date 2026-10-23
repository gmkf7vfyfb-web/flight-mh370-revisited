cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
p=open("prereg.py").read()
old=p[p.index("A1 (22 Oct, before any seed was run; plumbing only)"):p.index('"""\nfrom __future__')]
new='''A1 (22 Oct, before any seed was run): the impacts32 column latent:impact_energy_transferred_j is NaN in every run J row, so E is
   read from the tau90 sidecar's energy_transferred_j, then that column, then 0.5 m v^2 (counted). VALUE CHECK: on three seeds
   (waypoints 1, free 1, descent-climb 1) the sidecar equals 0.5 m v^2 on every row to within 6e-8 relative (float32 rounding),
   as the brief states (energy transferred = total kinetic energy, an upper anchor), so the E values are the same as the
   section 5 definition would have produced through its fallback; the source order changed, the numbers did not.
   CHUNK_ROWS 1 M -> 500 k (memory; no value change).
'''
p=p.replace(old,new); open("prereg.py","w").write(p); print("ok")
EOF
grep -n "A1 (22 Oct" -A 6 prereg.py | head -8
cd repo && M="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; mkdir -p "$M/data/stub"
cp ../hydro/stub/bathy_air9_*.csv ../hydro/stub/ssp_air9_*.csv ../hydro/stub/stub-manifest.json "$M/data/stub/"
cat > "$M/data/stub/PROVISIONAL.txt" <<'EOF'
PROVISIONAL ocean-environment stub - approved 2026-10-09 (coordination/HYDROACOUSTICS.md, morning rulings,
item 5). Two paths only: air9 -> H01W and air9 -> H08S. Built by prepare/build_path_stub.py (assumptions in
its docstring and in coordination/OCEAN_TRANSPORT.md, 2026-10-09). DELETE this directory when the shared
ocean-transport API serves sound-speed profiles and path bathymetry. Every number derived from it is
provisional. The WOA23 subset netCDF (1.35 MB) is kept as a project artifact, not committed.
GEBCO_2026: DOI 10.5285/4f68d5c7-45eb-f999-e063-7086abc0b9f6 per the dataset's own metadata (verify on citation).
EOF
python3 -c "import xarray" 2>/dev/null; git add "$M/data/stub" "$M/prepare/build_path_stub.py"
git diff --cached --name-only | grep -v 'engine/hypotheses/hydroacoustics/'; du -sh "$M/data/stub"
git commit -q -m "Hydroacoustics: provisional WOA23 (95A4, season 16) + GEBCO_2026 path stub for air9 -> H01W and air9 -> H08S, as ruled; no blockage on either path" && timeout 60 git push -q origin hypothesis/hydroacoustics && git log --oneline -1
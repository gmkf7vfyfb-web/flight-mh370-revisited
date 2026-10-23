cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib; p=pathlib.Path('tl_grid_ram_subset.py'); s=p.read_text()
s=s.replace('SUBSET = [("H01W", -33.0), ("H08S", -35.0), ("H08N", -32.0), ("3315", -36.0), ("3376", -25.0), ("3274", -36.0), ("3275", -40.0), ("3250", -24.0)]',
            'SUBSET = [("H01W", -33.0), ("H08S", -35.0), ("H08N", -32.5), ("3315", -36.0), ("3376", -38.5), ("3274", -38.0), ("3275", -40.0), ("3250", -24.0)]')
s=s.replace("  H01W 33.0 S, H08S 35.0 S, H08N 32.0 S, 3315 36.0 S, 3376 25.0 S, 3274 36.0 S, 3275 40.0 S, 3250 24.0 S.",
            "  H01W 33.0 S (corridor min 1,499 m), H08S 35.0 S (1,191 m, Broken Ridge / Ninetyeast crossing), H08N 32.5 S (24 m bank), 3315 36.0 S,\n  3376 38.5 S, 3274 38.0 S, 3275 40.0 S, 3250 24.0 S (North West Shelf).")
p.write_text(s)
EOF
python -c "import ast; ast.parse(open('tl_grid_ram_subset.py').read()); print('ok')"
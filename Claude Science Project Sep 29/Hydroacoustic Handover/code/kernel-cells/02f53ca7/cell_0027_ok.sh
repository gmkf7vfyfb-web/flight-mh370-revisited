cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import re
s=open('tl_recal_block9.py').read()
s=s.replace('''    for st in STATIONS:
        log[f"shared_air9_{st}"] = SP.convert(Path(shared_products), out / "shared", f"air9-{st}") if (out / "shared").mkdir(parents=True, exist_ok=True) is None else None''','''    (out / "shared").mkdir(parents=True, exist_ok=True)
    for st in STATIONS:
        log[f"shared_air9_{st}"] = SP.convert(Path(shared_products), out / "shared", f"air9-{st}")''')
open('tl_recal_block9.py','w').write(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal; mkdir -p $W
time python tl_recal_block9.py sections "$PWD/../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-audit/scripts" /Users/pete/Downloads/mh370-ocean-data/products/hydro-paths-2001-10 $W/sections 2>&1 | tail -40
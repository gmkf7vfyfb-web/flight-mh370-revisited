cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "^import\|^from\|B = \|as B" exploratory/pleiades_test/lhyd.py | head
grep -rn "def band_fraction" --include=*.py . | head -3
f=$(grep -rln "def band_fraction" --include=*.py . | head -1); python - "$f" <<'EOF'
import sys,re
src=open(sys.argv[1]).read()
i=src.find("def band_fraction"); print(src[i-1500:i+1200])
EOF
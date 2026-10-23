cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -rn "woa23\|_c_mean\|memmap\|reshape" --include=*.py . | grep -i "woa\|c_mean\|f32" | head -10
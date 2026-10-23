cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
s=open("reduce.py").read()
s=s.replace('''    return arr1deg[..., i0:i1 + 1].sum(-1) if lo > -41 or hi < -20 else arr1deg[..., 1:22].sum(-1)''','''    return arr1deg[i0:i1 + 1].sum(0)      # band axis is the first axis ([band] or [band, eta])''')
open("reduce.py","w").write(s)
EOF
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging && OMP_NUM_THREADS=1 timeout 900 python reduce.py $S /tmp/b11test 2>&1 | grep -v Warn | tail -30; ls /tmp/b11test
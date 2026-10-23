mkdir -p build/kval && cd build/kval
cat > ideal.env <<'EOF'
'ideal waveguide: vacuum surface, rigid bottom, c=1500'
50.0
1
'CVW'
2000  0.0  100.0
    0.0  1500.0  0.0  1.0  0.0  0.0
  100.0  1500.0 /
'R' 0.0
0.0  1.0e9
0
1
50 /
1
50 /
EOF
../at_src/at/Kraken/kraken.exe ideal > /dev/null 2>&1; echo rc=$?
python - <<'EOF'
import re, numpy as np
txt=open("ideal.prt").read()
rows=re.findall(r"^\s+(\d+)\s+([\d.Ee+-]+)\s+[-\d.Ee+]+\s+([\d.]+)\s+([\d.]+)\s*$", txt, re.M)
k=np.array([float(r[1]) for r in rows]); n=np.array([int(r[0]) for r in rows])
w=2*np.pi*50; H=100; c=1500
ka=np.sqrt((w/c)**2-((n-0.5)*np.pi/H)**2)
print("modes", len(k), "analytic count", int(np.floor(2*H*50/c+0.5)))
print("max |dk|/k", np.max(np.abs(k-ka)/ka))
print("f_c=c/4H", c/(4*H), "Hz -> mode 1 exists above 3.75 Hz")
EOF
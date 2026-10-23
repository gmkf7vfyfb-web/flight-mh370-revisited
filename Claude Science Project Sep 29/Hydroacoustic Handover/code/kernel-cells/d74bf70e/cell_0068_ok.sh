cd build/kval
for m in 500 2000 8000; do sed "s/^2000 /$m /" ideal.env > i$m.env; ../at_src/at/Kraken/kraken.exe i$m >/dev/null 2>&1
python - "$m" <<'EOF'
import re,sys,numpy as np
t=open(f"i{sys.argv[1]}.prt").read()
r=re.findall(r"^\s+(\d+)\s+([\d.Ee+-]+)\s+[-\d.Ee+]+\s+([\d.]+)\s+([\d.]+)\s*$",t,re.M)
k=np.array([float(x[1]) for x in r]); n=np.arange(1,len(k)+1)
ka=np.sqrt((2*np.pi*50/1500)**2-((n-0.5)*np.pi/100)**2)
print(sys.argv[1], len(k), f"{np.max(np.abs(k-ka)/ka):.2e}")
EOF
done
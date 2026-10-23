python - <<'EOF'
import re
t=open('/tmp/nielsen2020.pdf.txt').read().replace('\r','')
for m in re.finditer(r'dB',t):
    s=max(0,m.start()-250); print('...',t[s:m.end()+150].replace('\n',' ')); print()
EOF
ls "repo/Claude Science Project Sep 29/results/hydroacoustics-audit/"; 
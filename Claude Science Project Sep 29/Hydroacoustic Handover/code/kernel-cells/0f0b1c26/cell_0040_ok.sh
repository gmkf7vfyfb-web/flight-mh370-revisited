python - <<'EOF'
import re
t=open('/tmp/vergoz2021.pdf.txt').read()
for kw in ['139 dB','134 dB','predicted attenua','132 dB','Rio Grande Rise (signal','divided by 10','108 kg','Fig. 4','Figure 4']:
    for m in re.finditer(re.escape(kw),t):
        s=max(0,m.start()-700); print('-----',kw); print(t[s:m.end()+500].replace('\r',''))
        break
EOF
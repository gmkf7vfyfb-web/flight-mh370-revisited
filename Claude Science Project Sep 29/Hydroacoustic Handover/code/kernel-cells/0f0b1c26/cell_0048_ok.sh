python - <<'EOF'
t=open('/tmp/nielsen2020.pdf.txt').read().replace('\r','')
import re
i=t.find('Calibrated signal spectrum')
print(t[i-2500:i+1500])
EOF
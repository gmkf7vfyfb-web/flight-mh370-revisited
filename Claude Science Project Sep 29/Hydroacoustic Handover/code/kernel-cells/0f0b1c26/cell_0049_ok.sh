python - <<'EOF'
t=open('/tmp/nielsen2020.pdf.txt').read().replace('\r','')
for kw in ['PSD','time window','window','duration of']:
    import re
    for m in list(re.finditer(kw,t))[:6]:
        print('...',t[max(0,m.start()-300):m.end()+250].replace('\n',' '));print()
EOF
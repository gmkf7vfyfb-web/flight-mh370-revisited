python - <<'EOF'
import re,html
t=open('contrail/370loc.html').read()
t=re.sub(r'<(script|style).*?</\1>','',t,flags=re.S|re.I)
c=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t)))
i=c.find('Feb 2017 Update'); print(c[i:i+3500])
EOF
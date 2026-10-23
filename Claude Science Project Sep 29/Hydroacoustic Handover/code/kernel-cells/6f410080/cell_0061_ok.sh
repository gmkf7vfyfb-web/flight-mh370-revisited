python - <<'EOF'
import re,html
t=open('contrail/wg_contrail.shtml').read()
c=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<(script|style).*?</\1>','',t,flags=re.S))))
i=c.find('which would produce this contrail'); print(c[i:i+5000])
EOF
cd handoff/ck18 && python - <<'EOF'
import re,html,glob
f=glob.glob('**/iannello_2024_proposal.html',recursive=True)[0]
t=open(f,errors='ignore').read()
c=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<(script|style).*?</\1>','',t,flags=re.S))))
print(c[:300])
for m in re.finditer(r'[Cc]ontrail',c): print('..',c[max(0,m.start()-500):m.start()+500])
EOF
cd src; python - <<'EOF'
import re,html
t=open('GafferTape_OceanShield.html',encoding='utf-8',errors='ignore').read()
t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S); t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
i=t.find('Gaffer'); print(len(t))
for m in re.finditer(r'(\d{1,2}[.°]\d*\s*°?\s*S)|33\.\d+ ?kHz|Zenith|km2|square', t):
    pass
idx=[m.start() for m in re.finditer(r'kHz|°S|degrees south|author|Posted|By ', t)][:5]
print(t[:300]); 
for k in ['Posted','Author','kHz']:
    j=t.find(k); print(k, t[max(0,j-300):j+600] if j>=0 else None); print('---')
EOF
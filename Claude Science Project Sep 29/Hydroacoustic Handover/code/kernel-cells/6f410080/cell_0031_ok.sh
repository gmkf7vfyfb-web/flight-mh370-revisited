python - <<'EOF'
import requests,re,time,os
items=[('http://www.weathergraphics.com:80/malaysia/contrail.shtml','20140322124712'),('http://www.weathergraphics.com:80/malaysia/iozooms.shtml','20140321162636'),('http://www.weathergraphics.com:80/malaysia/index.shtml','20140322153831')]
for u,ts in items:
    for a in range(3):
        r=requests.get(f'http://web.archive.org/web/{ts}id_/{u}',timeout=90)
        if r.status_code==200: break
        time.sleep(5)
    fn='contrail/wg_'+u.split('/')[-1]
    open(fn,'w').write(r.text); print(fn,r.status_code,len(r.text))
EOF
python - <<'EOF'
import re,html
for f in ['contrail/wg_contrail.shtml','contrail/wg_iozooms.shtml','contrail/wg_index.shtml']:
    t=open(f).read()
    imgs=re.findall(r'src="([^"]+)"',t,re.I)
    txt=re.sub(r'<script.*?</script>','',t,flags=re.S|re.I)
    txt=html.unescape(re.sub(r'<[^>]+>',' ',txt)); txt=re.sub(r'\s+',' ',txt)
    print('#####',f,'\nIMGS',imgs[:60]); print(txt[:6000])
EOF
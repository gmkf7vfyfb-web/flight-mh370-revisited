cd rr/drive; python - <<'EOF' 2>/dev/null
import pypdf
for f in ['atsb_search_areas.pdf','bharat_rakshak.pdf','iannello_safety_report.pdf']:
    r=pypdf.PdfReader(f); t='\n'.join(f'=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(r.pages)); open(f[:-4]+'.txt','w').write(t); print(f,len(r.pages))
EOF
head -40 atsb_search_areas.txt
grep -n -i -E "indonesia|other aircraft|other traffic|EK343|emirates|MEKAR|N571|infrasound|CTBTO|Thai|India" atsb_search_areas.txt | head -40
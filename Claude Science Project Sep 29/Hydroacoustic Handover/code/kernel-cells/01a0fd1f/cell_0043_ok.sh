cd rr; python - <<'EOF' 2>/dev/null
import pypdf
for f in ['ucrl.pdf','stead.pdf']:
    r=pypdf.PdfReader(f); t='\n'.join(f'=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(r.pages)); open(f[:-4]+'.txt','w').write(t); print(f,len(r.pages),len(t))
EOF
grep -n -i -E "cocos|keeling|infrasound|T-phase|t-wave station|seismic station|receiver|recorded at|H06|IS06|I06|XMI|COCO" ucrl.txt | head -40
echo ======; grep -n -i -E "cocos|infrasound|I06|IS06|COCO|AIS|station" stead.txt | head -40
cd rr; python - <<'EOF' 2>/dev/null
import pypdf
r=pypdf.PdfReader('royer2016.pdf'); print(len(r.pages))
t='\n'.join(f'=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(r.pages)); open('royer2016.txt','w').write(t); print(len(t))
EOF
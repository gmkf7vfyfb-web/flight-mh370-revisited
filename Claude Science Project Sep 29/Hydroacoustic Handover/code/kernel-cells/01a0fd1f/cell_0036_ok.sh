cd rr
curl -sL -m 120 -o mis2014.pdf "https://archimer.ifremer.fr/doc/01032/114374/129113.pdf"; curl -sL -m 120 -o mis2015.pdf "https://archimer.ifremer.fr/doc/01032/114375/129114.pdf"; ls -la mis2014.pdf mis2015.pdf
python - <<'EOF' 2>/dev/null
import pypdf
for f in ['mis2014.pdf','mis2015.pdf']:
    r=pypdf.PdfReader(f); t='\n'.join(f'=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(r.pages)); open(f[:-4]+'.txt','w').write(t); print(f,len(r.pages),len(t))
EOF
grep -n -i -E "NEAMS|NE-AMS|SWAMS|MAD|NCRO|WKER|SSEIR|largu|mouill|récup|deploy|immersion|profondeur|échantill|240|hydrophone" mis2014.txt | head -60
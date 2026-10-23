cd repo; python3 - <<'EOF'
import base64,zipfile,io,binascii
s=''.join(open("Sept 27 2026 backup PL ChatGPT instance/Blackman_2004_extracted_data_2026-09-27.zip.b64").read().split())
print(len(s), set(c for c in s if not (c.isalnum() or c in '+/=')))
ok=[]
for i in range(len(s)):
    t=s[:i]+s[i+1:]
    try: b=base64.b64decode(t,validate=True)
    except binascii.Error: continue
    try:
        z=zipfile.ZipFile(io.BytesIO(b))
        if z.testzip() is None: ok.append(i)
    except Exception: pass
    if len(ok)>3: break
print(ok[:5])
EOF
cd repo
P="Sept 27 2026 backup PL ChatGPT instance/Blackman_2004_extracted_data_2026-09-27.zip.b64"
timeout 120 git show "HEAD:$P" > /tmp/b64.txt && wc -c /tmp/b64.txt && shasum -a 256 /tmp/b64.txt | cut -c1-64
python3 - <<'EOF'
import base64,hashlib,zipfile,io
s=open('/tmp/b64.txt').read().replace('\n','')
print("chars", len(s))
r=s[:13597]+'G'+s[13597:]
z=base64.b64decode(r); print("zip bytes", len(z), "sha256", hashlib.sha256(z).hexdigest())
zf=zipfile.ZipFile(io.BytesIO(z)); print("crc ok:", zf.testzip() is None, "entries", len(zf.namelist()))
EOF
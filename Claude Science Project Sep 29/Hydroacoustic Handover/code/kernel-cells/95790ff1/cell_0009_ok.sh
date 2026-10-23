cd repo; python3 - <<'EOF'
import base64,zipfile,io,binascii
s=''.join(open("Sept 27 2026 backup PL ChatGPT instance/Blackman_2004_extracted_data_2026-09-27.zip.b64").read().split())
A='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
lo=8622*4//3-8; hi=(10276*4)//3+8
sols=[]
for i in range(lo,hi):
    for c in A:
        t=s[:i]+c+s[i:]
        try:
            z=zipfile.ZipFile(io.BytesIO(base64.b64decode(t)))
            if z.testzip() is None: sols.append((i,c,t))
        except Exception: pass
print(len(sols), [(i,c) for i,c,_ in sols[:10]])
if sols:
    outs=set(base64.b64decode(t) for _,_,t in sols); print('distinct zips',len(outs))
    import pathlib; pathlib.Path('../prior/b.zip').write_bytes(base64.b64decode(sols[0][2]))
EOF
cd ../prior && unzip -o -q b.zip && ls -l Blackman_2004_extracted_data
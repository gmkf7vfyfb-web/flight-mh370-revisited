cd repo; f="Sept 27 2026 backup PL ChatGPT instance/Blackman_2004_extracted_data_2026-09-27.zip.b64"; head -c 300 "$f"; echo; tail -c 200 "$f"; echo; wc -l "$f"; python3 -c "
import base64,zipfile,io,sys
s=open(sys.argv[1]).read()
b=base64.b64decode(''.join(s.split()), validate=False)
print(len(b), b[:4], b[-22:])
" "$f"
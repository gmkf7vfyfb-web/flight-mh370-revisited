"""Verify every manifest entry, then create a self-contained offline rerun archive."""
from pathlib import Path
import csv,hashlib,zipfile
B=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((B/'FILE_MANIFEST.csv').open()))
for r in rows:
    p=B/r['path']
    assert p.stat().st_size==int(r['bytes'])
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
out=B.parent/'mh370_conditional_reverse_drift_v1.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for r in rows:z.write(B/r['path'],arcname='reverse_drift_v1/'+r['path'])
    z.write(B/'FILE_MANIFEST.csv',arcname='reverse_drift_v1/FILE_MANIFEST.csv')
with zipfile.ZipFile(out) as z:assert z.testzip() is None
h=hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.zip.sha256').write_text(h+'  '+out.name+'\n')
print('Verified entries',len(rows),'archive bytes',out.stat().st_size,'SHA-256',h)

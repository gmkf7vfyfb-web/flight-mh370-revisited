
OLDH='b5712a95fc2f29b81ea176b5ef7d7aa87191544a2588a483951c718c1c678e9c'; NEWH=sha(new_md); NEWN=len(new_md)
def fix_manifest(txt):
    out=[]
    for l in txt.split('\n'):
        if re.search(r'\bREQUESTS\.txt\b',l) and l.startswith(OLDH):
            l=re.sub(r'^[0-9a-f]{64}\s+\d+', NEWH+str(NEWN).rjust(11), l)
        out.append(l)
    return '\n'.join(out)
# exchange folder
open(os.path.join(X,'REQUESTS.md'),'wb').write(new_md)
mf_t=open(os.path.join(X,'MANIFEST.txt')).read(); open(os.path.join(X,'MANIFEST.txt'),'w').write(fix_manifest(mf_t))
sums=open(os.path.join(X,'SHA256SUMS')).read()
sums2='\n'.join((NEWH+l[64:] if (l.startswith(OLDH) and 'REQUESTS' in l) else l) for l in sums.split('\n'))
assert sums2!=sums; open(os.path.join(X,'SHA256SUMS'),'w').write(sums2)
# SHA256SUMS may also list MANIFEST.txt: refresh its hash if so
if re.search(r'  MANIFEST\.txt',sums2):
    mh=sha(open(os.path.join(X,'MANIFEST.txt'),'rb').read())
    sums3='\n'.join((mh+l[64:] if l.rstrip().endswith('MANIFEST.txt') else l) for l in sums2.split('\n'))
    open(os.path.join(X,'SHA256SUMS'),'w').write(sums3)
# zip: rewrite with replaced REQUESTS.md and MANIFEST.txt
zp=os.path.join(X,'kadri-package-v2-2026-10-22.zip'); tmp=zp+'.new'
with zipfile.ZipFile(zp) as zin, zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        data=zin.read(it.filename)
        if it.filename.endswith('/REQUESTS.md'): data=new_md
        elif it.filename.endswith('/MANIFEST.txt'): data=fix_manifest(data.decode('utf-8')).encode('utf-8')
        zi=zipfile.ZipInfo(it.filename, date_time=it.date_time); zi.compress_type=zipfile.ZIP_DEFLATED; zi.external_attr=it.external_attr
        zout.writestr(zi,data)
os.replace(tmp,zp)
z2=zipfile.ZipFile(zp); print('zip entries', len(z2.namelist()), '| zip REQUESTS.md ok:', z2.read('kadri-package-v2/REQUESTS.md')==new_md)
# verify checksums in exchange folder
bad=[]
for l in open(os.path.join(X,'SHA256SUMS')).read().split('\n'):
    if not l.strip(): continue
    h,fn=l.split(None,1); fn=fn.strip()
    p=os.path.join(X,fn)
    if os.path.exists(p) and sha(open(p,'rb').read())!=h: bad.append(fn)
print('SHA256SUMS mismatches:', bad)

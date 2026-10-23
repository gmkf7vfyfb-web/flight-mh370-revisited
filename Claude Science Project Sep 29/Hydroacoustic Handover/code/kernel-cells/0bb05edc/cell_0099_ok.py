
zh=sha(open(zp,'rb').read())
lines=open(os.path.join(X,'SHA256SUMS')).read().split('\n')
lines=[(zh+l[64:] if l.rstrip().endswith('kadri-package-v2-2026-10-22.zip') else l) for l in lines]
open(os.path.join(X,'SHA256SUMS'),'w').write('\n'.join(lines))
bad=[]
for l in lines:
    if not l.strip(): continue
    h,fn=l.split(None,1); fn=fn.strip(); p=os.path.join(X,fn)
    if os.path.exists(p) and sha(open(p,'rb').read())!=h: bad.append(fn)
print('SHA256SUMS mismatches now:', bad)

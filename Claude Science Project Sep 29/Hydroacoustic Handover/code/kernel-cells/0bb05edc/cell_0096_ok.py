
import zipfile
X='/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2'
z=zipfile.ZipFile(os.path.join(X,'kadri-package-v2-2026-10-22.zip'))
names=z.namelist(); print(len(names), [n for n in names if 'REQUESTS' in n or 'MANIFEST' in n or 'SHA' in n])
print(open(os.path.join(X,'SHA256SUMS')).read()[:400])
print([l for l in open(os.path.join(X,'MANIFEST.txt')).read().split('\n') if 'REQUESTS' in l][0][:120])

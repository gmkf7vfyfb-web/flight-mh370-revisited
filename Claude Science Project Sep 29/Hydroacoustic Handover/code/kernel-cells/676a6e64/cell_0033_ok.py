import os, glob
r = host.artifacts(filename='acoustics-toolbox', limit=10)
for a in r['artifacts']: print(a['filename'], a['size_bytes'], a['latest_version_id'], a.get('created_at','')[:10])
# any local copy already?
for p in ['/Users/pete/Downloads/mh370-inputs/hydroacoustics', '/Users/pete/Downloads']:
    hits = glob.glob(p+'/**/kraken.exe', recursive=True)[:3]; print(p, hits)
r2 = host.artifacts(filename='hydroacoustics', limit=200)
print(r2['count'])
import collections
print(collections.Counter(a['filename'].rsplit('.',1)[-1] for a in r2['artifacts']).most_common(8))
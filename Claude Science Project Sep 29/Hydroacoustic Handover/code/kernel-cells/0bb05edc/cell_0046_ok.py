
import subprocess, csv, io, re, json, collections
REPO='/Users/pete/Downloads/flight-mh370-revisited'; B='origin/claude-science-sep29'; P='Claude Science Project Sep 29'
def show(path, ref=B):
    return subprocess.run(['git','-C',REPO,'show',f'{ref}:{path}'],capture_output=True,text=True).stdout
# 1. hydroacoustics bibliography
t = show(f'{P}/results/hydroacoustics-bibliography.csv').replace('\r','')
rows = list(csv.DictReader(io.StringIO(t)))
print(len(rows), rows[0].keys())
c = collections.Counter(r['open_access'] for r in rows); print(c)
c2 = collections.Counter(r['read_level'].split(' (')[0] for r in rows); print(c2.most_common(12))
flag = [r for r in rows if r['open_access'].lower() not in ('gold oa','hybrid oa','green oa','bronze oa','n/a','public','public record','open') or re.search(r'metadata|abstract|secondary|snippet',r['read_level'],re.I)]
print(len(flag))
for r in flag: print(r['key'],'|',r['year'],'|',r['title'][:60],'|',r['doi_or_url'][:40],'|',r['open_access'],'|',r['read_level'][:50])

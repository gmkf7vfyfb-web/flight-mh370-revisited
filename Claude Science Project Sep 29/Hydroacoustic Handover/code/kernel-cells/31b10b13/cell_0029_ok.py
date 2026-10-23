
import itertools, collections
adj=collections.defaultdict(set)
for a,b in zip(PRS.cid_a,PRS.cid_b): adj[a].add(b); adj[b].add(a)
rxof=lambda c: c.split("|")[0]
tri=set()
for a in adj:
    for b,c in itertools.combinations(sorted(adj[a]),2):
        if c in adj[b] and len({rxof(a),rxof(b),rxof(c)})==3: tri.add(tuple(sorted((a,b,c))))
tri=sorted(tri); print(len(tri), collections.Counter(tuple(sorted(rxof(x) for x in t)) for t in tri).most_common(20))

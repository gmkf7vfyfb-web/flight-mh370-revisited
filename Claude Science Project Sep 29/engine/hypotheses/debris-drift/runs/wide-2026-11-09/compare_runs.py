"""Identity checks for the restrict_to_classes patch (python3 stdlib). Usage: compare_runs.py DIR_A DIR_B MODE
MODE 'bytes': same files byte for byte (old binary vs patched binary, default config).
MODE 'class1': every coefficient record of class index 1 (exterior) equal between the unrestricted run (A) and the restricted run (B); classes 0 and 2 empty in B."""
import sys, json, hashlib, os
a, b, mode = sys.argv[1:4]
def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''): h.update(ch)
    return h.hexdigest()
out = {}
if mode == 'bytes':
    for f in ('nodes.csv', 'coefficients.jsonl', 'coefficients-meta.json', 'responses.json', 'arrivals.bin', 'summary.toml'):
        pa, pb = os.path.join(a, f), os.path.join(b, f)
        out[f] = dict(a=md5(pa) if os.path.exists(pa) else None, b=md5(pb) if os.path.exists(pb) else None, size=os.path.getsize(pa) if os.path.exists(pa) else None)
        out[f]['identical'] = out[f]['a'] == out[f]['b'] and out[f]['a'] is not None
else:
    A = [json.loads(l) for l in open(os.path.join(a, 'coefficients.jsonl'))]; B = [json.loads(l) for l in open(os.path.join(b, 'coefficients.jsonl'))]
    assert [x['node'] for x in A] == [x['node'] for x in B]
    n = 0; same = 0; other_empty = True; keys = set()
    for x, y in zip(A, B):
        for sx, sy in zip(x['sets'], y['sets']):
            for part in sx:
                for env_x, env_y in zip(sx[part], sy[part]):
                    n += 1; keys.add(part)
                    if env_x[1] == env_y[1]: same += 1
                    for c in (0, 2):
                        e = env_y[c]
                        if e is not None and (e.get('a') and any(len(r) for r in e['a'])): other_empty = False
    out = dict(records_compared=n, class1_identical=same, all_identical=(n == same), classes_0_2_empty_in_restricted=other_empty, parts=sorted(keys))
    ma = json.load(open(os.path.join(a, 'coefficients-meta.json'))); mb = json.load(open(os.path.join(b, 'coefficients-meta.json')))
    out['meta_finds_a'] = [f['id'] for f in ma['finds']]; out['meta_finds_b'] = [f['id'] for f in mb['finds']]
    out['meta_shadow_a'] = len(ma['shadow_finds']); out['meta_shadow_b'] = len(mb['shadow_finds'])
print(json.dumps(out, indent=1))

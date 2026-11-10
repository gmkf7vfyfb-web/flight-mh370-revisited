"""Hybrid rescored coefficients: classes 0 (flaperon) and 2 (interior) from the production run (R3 rescore output), class 1 (exterior) from a rescored wide-windage run.
Usage: build_hybrid.py R3_DIR WIDE_DIR OUT_DIR [LEG_PREFIX_MAP]   (files ext-<model>-N.jsonl <-> wide-<model>-N.jsonl, ext2- <-> wide2-)
Checks: same nodes, same ocean-sample seeds, same number of class-1 finds and class totals length. Writes one line per node in the layout of the module's coefficient file."""
import json, sys, os, glob
R3, WD, OUT = sys.argv[1:4]; PRE = dict(x.split('=') for x in sys.argv[4:]) if len(sys.argv) > 4 else {'ext-': 'wide-', 'ext2-': 'wide2-'}
os.makedirs(OUT, exist_ok=True); nrec = 0; nchg = 0
for f in sorted(glob.glob(os.path.join(R3, '*.jsonl'))):
    base = os.path.basename(f); wb = next(base.replace(a, b, 1) for a, b in PRE.items() if base.startswith(a)); wf = os.path.join(WD, wb)
    with open(f) as fa, open(wf) as fb, open(os.path.join(OUT, base), 'w') as fo:
        for la, lb in zip(fa, fb):
            a = json.loads(la); b = json.loads(lb)
            assert a['node'] == b['node'] and a['env_seeds'] == b['env_seeds'] and len(a['sets']) == len(b['sets']), (base, a['node'], b['node'])
            for sa, sb in zip(a['sets'], b['sets']):
                for part in ('full', 'half_a', 'half_b'):
                    for ea, eb in zip(sa[part], sb[part]):
                        assert eb[1] is not None and len(ea[1]['a']) == len(eb[1]['a']) and len(ea[1]['A']) == len(eb[1]['A']), (base, a['node'])
                        ea[1] = eb[1]; nchg += 1
            fo.write(json.dumps(a, separators=(',', ':')) + '\n'); nrec += 1
        assert fb.readline() == '' and fa.readline() == ''
print('nodes', nrec, 'class-1 entries replaced', nchg)

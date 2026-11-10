"""Hybrid coefficients for one windage target (10 Nov 2026): classes 0 (flaperon) and 2 (interior) from the production R3 rescoring (first bandwidth, 50 km),
class 1 (exterior) from the reweighted wide legs (reweight_rescore.py output, 'full' part only, bandwidth 50 km).
Usage: build_hybrid_grid.py R3_DIR REWEIGHT_DIR OUT_DIR [PREFIX_MAP ...]   REWEIGHT_DIR holds <wide-leg>.jsonl.gz ; default map ext-=wide- ext2-=wide2- ext3-=wide3-
Production files without a counterpart in REWEIGHT_DIR (e.g. ext3-) are skipped. A third file family ext3-<model>-N (wide3 legs, all three classes simulated) has no production counterpart:
its classes 0 and 2 are taken from the wide3 rescoring itself (production windage for those classes), class 1 from the reweighting.
The halves are emptied ('full' only).  Checks: same nodes, same ocean-sample seeds, same number of find and period entries."""
import json, sys, os, glob, gzip
R3, RW, OUT = sys.argv[1:4]; PRE = dict(x.split('=') for x in sys.argv[4:]) if len(sys.argv) > 4 else {'ext-': 'wide-', 'ext2-': 'wide2-'}
os.makedirs(OUT, exist_ok=True); nrec = 0; nchg = 0; nfile = 0
def opn(p): return gzip.open(p, 'rt') if p.endswith('.gz') else open(p)
for pre, wpre in PRE.items():
    for wf in sorted(glob.glob(os.path.join(RW, wpre + '*.jsonl.gz'))):
        wbase = os.path.basename(wf)[:-3]; base = wbase.replace(wpre, pre, 1)
        pf = os.path.join(R3, base)
        with opn(wf) as fb, open(os.path.join(OUT, base), 'w') as fo:
            fa = open(pf) if os.path.exists(pf) else None
            for lb in fb:
                b = json.loads(lb)
                if fa is None:                      # no production counterpart: the rescoring itself supplies all classes
                    a = b
                else:
                    a = json.loads(fa.readline())
                    assert a['node'] == b['node'] and a['env_seeds'] == b['env_seeds'], (base, a['node'], b['node'])
                    a['sets'] = a['sets'][:1]
                    for sa, sb in zip(a['sets'], b['sets']):
                        sa['half_a'] = []; sa['half_b'] = []
                        for ea, eb in zip(sa['full'], sb['full']):
                            assert eb[1] is not None and len(ea[1]['a']) == len(eb[1]['a']) and len(ea[1]['A']) == len(eb[1]['A']), (base, a['node'])
                            ea[1] = eb[1]; nchg += 1
                fo.write(json.dumps(a, separators=(',', ':')) + '\n'); nrec += 1
            if fa is not None: assert fa.readline() == ''; fa.close()
        nfile += 1
print('files', nfile, 'nodes', nrec, 'class-1 entries replaced', nchg)

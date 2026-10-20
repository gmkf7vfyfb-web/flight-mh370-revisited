"""Stdlib-only aggregation of snapshots binary -> sparse 0.5-deg counts (deskstar has no numpy)."""
import struct, sys, json, math, collections
fn, ntimes, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rs = 16 + 8 * ntimes; fmt = '<4B3f' + 'f' * (2 * ntimes)
cell = lambda lo, la: (int(math.floor(lo * 2)), int(math.floor(la * 2)))
afloat = collections.defaultdict(collections.Counter); beach = collections.defaultdict(collections.Counter)
fate = collections.defaultdict(collections.Counter); beachday = collections.defaultdict(list); nrel = collections.Counter()
with open(fn, 'rb') as f:
    while True:
        b = f.read(rs * 4096)
        if not b: break
        for off in range(0, len(b), rs):
            v = struct.unpack_from(fmt, b, off); r, e, c, fc, bt, blo, bla = v[:7]; nrel[r] += 1; fate[r][fc] += 1
            if not math.isnan(bt): beach[r][cell(blo, bla) + (int(bt),)] += 1
            for k in range(ntimes):
                lo, la = v[7 + 2 * k], v[8 + 2 * k]
                if not math.isnan(lo): afloat[(r, k)][cell(lo, la)] += 1
res = {'n': dict(nrel), 'fate': {r: dict(x) for r, x in fate.items()},
       'afloat': {f'{r}|{k}': [[a, b, n] for (a, b), n in x.items()] for (r, k), x in afloat.items()},
       'beach': {str(r): [[a, b, d, n] for (a, b, d), n in x.items()] for r, x in beach.items()}}
json.dump(res, open(out, 'w')); print('ok', sum(nrel.values()))

"""Aggregate harness v2 records by (group, env): group 0 = release 0 (mode), 1 = all others. Usage: aggregate3.py BIN NTIMES OUT"""
import struct, sys, json, math, collections
fn, nt, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
rs = 20 + 16 * nt; fmt = '<4BHH3f' + 'f' * (4 * nt); cell = lambda lo, la: (int(math.floor(lo * 2)), int(math.floor(la * 2)))
A = collections.defaultdict(collections.Counter); O = collections.defaultdict(collections.Counter); B = collections.defaultdict(collections.Counter)
F = collections.defaultdict(collections.Counter); N = collections.Counter(); EP = collections.defaultdict(collections.Counter)
with open(fn, 'rb') as f:
    while True:
        b = f.read(rs * 4096)
        if not b: break
        for off in range(0, len(b), rs):
            v = struct.unpack_from(fmt, b, off); r, e, c, fc, ne, _, bt, blo, bla = v[:9]; g = 0 if r == 0 else 1; ge = f'{g}|{e}'
            N[ge] += 1; F[ge][fc] += 1; EP[ge][min(ne, 10)] += 1
            if not math.isnan(bt): B[ge][cell(blo, bla) + (int(bt),)] += 1
            for k in range(nt):
                lo, la, olo, ola = v[9 + 4 * k: 13 + 4 * k]
                if not math.isnan(lo): A[f'{ge}|{k}'][cell(lo, la)] += 1
                if not math.isnan(olo): O[f'{ge}|{k}'][cell(olo, ola)] += 1
d = lambda D: {k: [[*kk, n] for kk, n in x.items()] for k, x in D.items()}
json.dump({'n': dict(N), 'fate': {k: dict(x) for k, x in F.items()}, 'episodes': {k: dict(x) for k, x in EP.items()},
           'afloat': d(A), 'onshore': d(O), 'beach': d(B)}, open(out, 'w')); print('ok', sum(N.values()))

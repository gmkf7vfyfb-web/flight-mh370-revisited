"""Stdlib aggregation keyed by (group, env): group of a release given by a rule. Usage: aggregate2.py BIN NTIMES OUT RULE
RULE: 'identity' (group = release) or 'mode-vs-pdf' (release 0 -> 0, others -> 1)."""
import struct, sys, json, math, collections
fn, nt, out, rule = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
grp = (lambda r: r) if rule == 'identity' else (lambda r: 0 if r == 0 else 1)
rs = 16 + 8 * nt; fmt = '<4B3f' + 'f' * (2 * nt); cell = lambda lo, la: (int(math.floor(lo * 2)), int(math.floor(la * 2)))
A = collections.defaultdict(collections.Counter); B = collections.defaultdict(collections.Counter); F = collections.defaultdict(collections.Counter); N = collections.Counter()
with open(fn, 'rb') as f:
    while True:
        b = f.read(rs * 4096)
        if not b: break
        for off in range(0, len(b), rs):
            v = struct.unpack_from(fmt, b, off); r, e, c, fc, bt, blo, bla = v[:7]; g = grp(r); N[f'{g}|{e}'] += 1; F[f'{g}|{e}'][fc] += 1
            if not math.isnan(bt): B[f'{g}|{e}'][cell(blo, bla) + (int(bt),)] += 1
            for k in range(nt):
                lo, la = v[7 + 2 * k], v[8 + 2 * k]
                if not math.isnan(lo): A[f'{g}|{e}|{k}'][cell(lo, la)] += 1
json.dump({'n': dict(N), 'fate': {k: dict(x) for k, x in F.items()}, 'afloat': {k: [[a, b, n] for (a, b), n in x.items()] for k, x in A.items()},
           'beach': {k: [[a, b, d, n] for (a, b, d), n in x.items()] for k, x in B.items()}}, open(out, 'w')); print('ok', sum(N.values()))

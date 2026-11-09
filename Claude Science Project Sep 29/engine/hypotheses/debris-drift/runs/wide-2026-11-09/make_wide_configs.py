"""Build the wide-windage run configurations from the production legs (ext-*, ext2-*). Text-level edits only:
 1. exterior class renamed `wide_windage_exterior`, c_wind log-normal median 0.012, sigma 0.5, lo 0.003, hi 0.05 (wind angle unchanged);
 2. restrict_to_classes = [that class]: flaperon and interior finds are not scored, so those classes are not transported;
 3. the three shadow finds of other classes (flaperon-fresh-3d, flaperon-fresh-10d, identity-from-drift-riake-seat-back-trim) removed;
 4. splitting.classes renamed; output_dir -> runs/wide-<leg>.
Seeds (seed 21, env_seeds), nodes, ocean models, ocean error, diffusivity, offsets, levels, recovery: unchanged."""
import re, glob, os, sys
OLD = '''c_wind = { dist = "normal", mean = 0.012, sd = 0.003, lo = 0.005, hi = 0.02 }'''
NEW = '''c_wind = { dist = "log-normal", median = 0.012, sigma = 0.5, lo = 0.003, hi = 0.05 }'''
DROP = ('flaperon-fresh-3d', 'flaperon-fresh-10d', 'identity-from-drift-riake-seat-back-trim')
def convert(t, leg, outdir, restrict=True, wide=True):
    if wide:
        assert t.count(OLD) == 1; t = t.replace(OLD, NEW)
        assert t.count('name = "low_exposure_exterior"') == 1; t = t.replace('name = "low_exposure_exterior"', 'name = "wide_windage_exterior"')
        assert t.count('classes = ["low_exposure_exterior", "high_windage_interior"]') == 1
        t = t.replace('classes = ["low_exposure_exterior", "high_windage_interior"]', 'classes = ["wide_windage_exterior", "high_windage_interior"]')
        cls = 'wide_windage_exterior'
    else:
        cls = 'low_exposure_exterior'
    t, n = re.subn(r'output_dir = "[^"]*"', f'output_dir = "{outdir}"', t); assert n == 1
    if restrict:
        assert t.count('write_arrivals = true') == 1
        t = t.replace('write_arrivals = true', f'write_arrivals = true\nrestrict_to_classes = ["{cls}"]')
        blocks = re.split(r'(?=\[\[hypotheses\.debris-drift\.shadow_finds\]\])', t)
        keep = [blocks[0]]; dropped = 0
        for b in blocks[1:]:
            nm = re.search(r'name = "(.*?)"', b).group(1)
            if nm in DROP: dropped += 1; continue
            keep.append(b)
        assert dropped == sum(1 for _ in DROP) or dropped >= 0
        t = ''.join(keep)
    head = (f'# Wide-windage run, 9 Nov 2026 (Pete approved the design as proposed): exterior class c_wind log-normal median 0.012, sigma 0.5 (lo 0.003, hi 0.05),\n'
            f'# class `wide_windage_exterior`; restrict_to_classes keeps only exterior finds (flaperon and interior classes not transported); non-exterior shadow finds removed.\n'
            f'# All other settings identical to production leg {leg}. PROVISIONAL (windage prior).\n') if wide else \
           (f'# Identity test, 9 Nov 2026: production class definitions, restrict_to_classes = exterior only; coefficients of the exterior class must equal the unrestricted run exactly.\n')
    return head + t
if __name__ == '__main__':
    src = sys.argv[1]; dst = sys.argv[2]; os.makedirs(dst, exist_ok=True)
    legs = []
    for f in sorted(glob.glob(os.path.join(src, 'ext*-*.toml'))):
        leg = os.path.basename(f)[:-5]; new = leg.replace('ext2-', 'wide2-').replace('ext-', 'wide-')
        t = open(f).read(); out = convert(t, leg, f'/home/pete/mh370/drift/coef/runs/{new}')
        open(os.path.join(dst, new + '.toml'), 'w').write(out); legs.append((leg, new))
    for name in ('legs.txt', 'legs2.txt'):
        L = [l.strip() for l in open(os.path.join(src, name)) if l.strip()]
        open(os.path.join(dst, name), 'w').write('\n'.join(l.replace('ext2-', 'wide2-').replace('ext-', 'wide-') for l in L) + '\n')
    print(len(legs), 'legs written')

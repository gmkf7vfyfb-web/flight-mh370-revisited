"""Disk (architecture 11 Oct): keep in mini.npz only what the ln BF and family tables need; verify then replace atomically."""
import numpy as np, pathlib, os, re
W = pathlib.Path(__file__).resolve().parents[1]
KEEP = ["lw", "parent", "speed", "family_code", "ll:m0011", "ll:m0011+r600-bto", "ll:m0011+r600/no-offset", "ll:m0011+r600/inflated"]
for f in sorted(W.glob("abd/*-[AB]-s*/bto-bfo/seed-*/mini.npz")):
    m = re.match(r"(next-d-[a-z-]+)-[AB]-s(\d+)", f.parents[2].name)
    if not (W / "abd" / f"ab-{m.group(1)}-s{m.group(2)}-standin.json").exists(): continue
    z = np.load(f)
    if set(z.files) <= set(KEEP): continue
    d = {k: z[k] for k in KEEP if k in z.files}; tmp = f.with_name("mini.tmp.npz"); np.savez(tmp, **d)
    y = np.load(tmp); assert all(np.array_equal(y[k], d[k], equal_nan=True) for k in d); os.replace(tmp, f); print("trimmed", f.parents[2].name)

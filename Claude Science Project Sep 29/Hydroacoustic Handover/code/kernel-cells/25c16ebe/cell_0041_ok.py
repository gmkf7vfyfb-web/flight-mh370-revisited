mp = open("audit/end-of-flight.md").read()
import re
probes = {
 "support change / model reach": r"support change|reach|widen|exclusion",
 "proposal vs prior": r"proposal-only|proposal only|prior|importance",
 "held-out re-validation": r"held out|held-out",
 "top weight share": r"top weight|largest weight|weight share",
 "uniform-prior recovery test": r"uniform|self-check|self check|correction",
 "sidecar / in-sample emission": r"sidecar|same file|impacts\.npy|impacts32",
 "energy partition": r"partition|transferred|dissipat",
 "boundary threshold": r"boundary",
 "gate wording": r"\bgate\b",
 "control weights per family": r"control weights|per family",
}
for k,p in probes.items():
    hits = [m.start() for m in re.finditer(p, mp, re.I)]
    print(f"{k:32s} {len(hits):3d} hits")
print("\n--- every sentence containing 'boundary' ---")
for m in re.finditer(r"[^.\n]*boundary[^.]*\.", mp, re.I): print(" *", " ".join(m.group(0).split()))
print("\n--- every sentence containing 'gate' ---")
for m in re.finditer(r"[^.\n]*\bgate\b[^.]*\.", mp, re.I): print(" *", " ".join(m.group(0).split()))

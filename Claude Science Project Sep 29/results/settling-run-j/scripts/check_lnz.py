"""Compare settling's per-seed ln Z (info json) with end of flight's published table-0019 seed_ln_Z. Usage: check_lnz.py info.json table.json [D list]"""
import sys, json
NAME = {"00:19 Held Out": "D0", "00:19 R600 BTO Only": "D1", "00:19 R600 BTO + Raw BFO": "D2", "00:19 R600 BTO + both BFOs as recorded": "D3",
        "00:19 R600 BTO + both BFOs, Holland transient bias added": "D4", "00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added": "D5"}
info = json.load(open(sys.argv[1])); tab = json.load(open(sys.argv[2]))["cells"]; Ds = sys.argv[3].split(",") if len(sys.argv) > 3 else list(NAME.values())
worst, n = 0.0, 0
for k, v in info["per_seed_lnZ"].items():
    st, name, cell = k.split("|"); D = NAME[name]
    if D not in Ds: continue
    key = f"{D} total q=0.333 (C2 silent)" if cell == "total" else f"{D}x{cell}"
    ref = sorted([x for x in tab[key]["seed_ln_Z"]], key=lambda x: int(x[1].split("-")[1]))
    assert len(ref) == len(v), (key, len(ref), len(v))
    for a, b in zip(v, ref): worst = max(worst, abs(a - b[2])); n += 1
print(f"compared {n} seed x cell values; max |settling - published| = {worst:.3e}")
sys.exit(0 if worst < 1e-6 else 3)

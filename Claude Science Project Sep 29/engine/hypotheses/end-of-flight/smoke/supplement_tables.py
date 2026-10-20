"""Markdown tables for the run J northern supplement results note (overnight order A).

    python supplement_tables.py FINAL_JSON PASS1_JSON > tables.md
"""
import json, sys

T = ["D0", "D1", "D2", "D3", "D4", "D5"]
TN = {"D0": "D0' 00:19 data not used", "D1": "D1 R600 BTO", "D2": "D2 R600 BTO + BFO", "D3": "D3 both BFOs as recorded",
      "D4": "D4 both BFOs, Holland transient bias added", "D5": "D5 R600 + R1200 BFO with start-up offset"}
B3 = ["35-30 S", "30-25 S", "25-20 S"]
P5 = {("D2", "35-30 S"): (1000, None), ("D2", "30-25 S"): (1000, None), ("D2", "25-20 S"): (1000, None),
      ("D4", "30-25 S"): (800, 2500), ("D4", "35-30 S"): (600, 1500), ("D3", "35-30 S"): (500, 1500), ("D3", "30-25 S"): (500, 1500)}


def band(S, d, w, name, b):
    return next(r for r in S["cells"][d][w][name]["bands"] if r["band"] == b)


def k(x):
    return f"{x/1000:.1f}k" if x >= 10000 else f"{x:,.0f}"


def main(fj, pj):
    F, P = json.load(open(fj)), json.load(open(pj))
    for name, lab in (("imp", "impact latitude"), ("h11", "00:11 latitude")):
        print(f"\n**Band ESS by {lab}: rows / parents / distinct 00:11 states** (target 1,000; production alone -> + supplement, 64 descents -> + extra descents)\n")
        print("| treatment | " + " | ".join(B3) + " |"); print("|---|" + "---|" * len(B3))
        for d in T:
            cells = []
            for b in B3:
                a = band(F, d, "alone", name, b)["all"]; p = band(P, d, "comb", name, b)["all"]; f = band(F, d, "comb", name, b)["all"]
                s = f"{k(a['rows'])}/{k(a['parents'])}/{k(a['states'])} -> {k(p['rows'])}/{k(p['parents'])}/{k(p['states'])}"
                if d in ("D2", "D3", "D4", "D5"): s += f" -> **{k(f['rows'])}/{k(f['parents'])}/{k(f['states'])}**"
                cells.append(s)
            print(f"| {TN[d]} | " + " | ".join(cells) + " |")
    print("\n**Family ESS by impact band (distinct 00:11 states), final combined set** (A1 = cruise to fuel exhaustion then no control; "
          "A2 = cruise to fuel exhaustion then controlled descent; B = planned descent begun before fuel exhaustion)\n")
    print("| treatment | " + " | ".join(f"{b} A1 / A2 / B" for b in B3) + " |"); print("|---|" + "---|" * len(B3))
    for d in T:
        print(f"| {TN[d]} | " + " | ".join(" / ".join(k(band(F, d, "comb", "imp", b)[f]["states"]) for f in ("A1", "A2", "B")) for b in B3) + " |")
    print("\n**P5, prediction by prediction** (impact band; distinct-state ESS, the most conservative measure; rows ESS in brackets)\n")
    print("| prediction | first pass (64 descents) | with extra descents | verdict (first pass, as P5 was stated) | verdict with extra descents |"); print("|---|---|---|---|---|")
    for (d, b), (lo, hi) in P5.items():
        p = band(P, d, "comb", "imp", b)["all"]; f = band(F, d, "comb", "imp", b)["all"]
        rng = f">= {lo:,}" if hi is None else f"{lo/1000:.1f}k-{hi/1000:.1f}k"
        def v(x): return "inside" if x >= lo and (hi is None or x <= hi) else ("below" if x < lo else "above")
        print(f"| {d} {b}: {rng} | {p['states']:,.0f} ({p['rows']:,.0f}) | {f['states']:,.0f} ({f['rows']:,.0f}) | {v(p['states'])} | {v(f['states'])} (>= 1,000: {'yes' if f['states'] >= 1000 else 'no'}) |")
    print("\n**Band masses (impact latitude), production alone vs combined, with 95 % seed-bootstrap intervals**\n")
    print("| treatment | " + " | ".join(B3 + ["north of 33 S", "north of 30 S"]) + " |"); print("|---|" + "---|" * 5)
    for d in T:
        c = F["cells"][d]; row = []
        for b in B3 + ["north of 33 S", "north of 30 S"]:
            if b in B3: va, vc = band(F, d, "alone", "imp", b)["mass"], band(F, d, "comb", "imp", b)["mass"]
            else: va, vc = c["north_alone"][b], c["north_comb"][b]
            ba, bc = c["boot_alone"][b], c["boot_comb"][b]
            row.append(f"{va:.4f} [{ba['q025']:.4f}, {ba['q975']:.4f}] -> {vc:.4f} [{bc['q025']:.4f}, {bc['q975']:.4f}]")
        print(f"| {TN[d]} | " + " | ".join(row) + " |")
    print("\n**Whole-posterior summaries, production alone -> combined**\n")
    print("| treatment | ln Z | A1 / A2 / B | impact latitude 5 / 50 / 95 % | 00:11 latitude 50 % |"); print("|---|---|---|---|---|")
    for d in T:
        a, c = F["cells"][d]["alone"], F["cells"][d]["comb"]
        fa = " / ".join(f"{a['imp']['families'][f]:.3f}" for f in ("A1", "A2", "B")); fc = " / ".join(f"{c['imp']['families'][f]:.3f}" for f in ("A1", "A2", "B"))
        qa = " / ".join(f"{x:.2f}" for x in a["imp"]["q05_q50_q95"]); qc = " / ".join(f"{x:.2f}" for x in c["imp"]["q05_q50_q95"])
        print(f"| {TN[d]} | {a['imp']['lnZ']:.3f} -> {c['imp']['lnZ']:.3f} | {fa} -> {fc} | {qa} -> {qc} | {a['h11']['q05_q50_q95'][1]:.2f} -> {c['h11']['q05_q50_q95'][1]:.2f} |")





def compare(after_json, before_json):
    """20 Oct: full supplement (both halves) against the 19 Oct k = 2 set, and production alone."""
    A, Bf = json.load(open(after_json)), json.load(open(before_json))
    for name, lab in (("imp", "impact latitude"), ("h11", "00:11 latitude")):
        print(f"\n**Band ESS by {lab}: rows / paths / distinct 00:11 states** (target 1,000; production alone -> 19 Oct, half the supplement -> **20 Oct, all supplement rows**)\n")
        print("| treatment | " + " | ".join(B3) + " |"); print("|---|" + "---|" * len(B3))
        for d in T:
            cells = []
            for b in B3:
                a = band(A, d, "alone", name, b)["all"]; p = band(Bf, d, "comb", name, b)["all"]; f = band(A, d, "comb", name, b)["all"]
                cells.append(f"{k(a['rows'])}/{k(a['parents'])}/{k(a['states'])} -> {k(p['rows'])}/{k(p['parents'])}/{k(p['states'])} -> **{k(f['rows'])}/{k(f['parents'])}/{k(f['states'])}**")
            print(f"| {TN[d]} | " + " | ".join(cells) + " |")
    print("\n**Family ESS by impact band (distinct 00:11 states), 19 Oct -> 20 Oct** (A1 = cruise to fuel exhaustion then no control; "
          "A2 = cruise to fuel exhaustion then controlled descent; B = planned descent begun before fuel exhaustion)\n")
    print("| treatment | " + " | ".join(f"{b} A1 / A2 / B" for b in B3) + " |"); print("|---|" + "---|" * len(B3))
    for d in T:
        print(f"| {TN[d]} | " + " | ".join(" / ".join(f"{k(band(Bf, d, 'comb', 'imp', b)[f]['states'])} -> {k(band(A, d, 'comb', 'imp', b)[f]['states'])}" for f in ("A1", "A2", "B")) for b in B3) + " |")
    print("\n**Band masses (impact latitude) with 95 % seed-bootstrap intervals: production alone -> 19 Oct -> 20 Oct**\n")
    print("| treatment | " + " | ".join(B3 + ["north of 33 S", "north of 30 S"]) + " |"); print("|---|" + "---|" * 5)
    for d in T:
        row = []
        for b in B3 + ["north of 33 S", "north of 30 S"]:
            def val(S, w):
                return band(S, d, w, "imp", b)["mass"] if b in B3 else S["cells"][d][f"north_{w}"][b]
            ba, bb, bc = A["cells"][d]["boot_alone"][b], Bf["cells"][d]["boot_comb"][b], A["cells"][d]["boot_comb"][b]
            row.append(f"{val(A, 'alone'):.4f} [{ba['q025']:.4f}, {ba['q975']:.4f}] -> {val(Bf, 'comb'):.4f} [{bb['q025']:.4f}, {bb['q975']:.4f}] -> **{val(A, 'comb'):.4f}** [{bc['q025']:.4f}, {bc['q975']:.4f}]")
        print(f"| {TN[d]} | " + " | ".join(row) + " |")
    print("\n**Whole-posterior summaries: production alone -> 20 Oct combined**\n")
    print("| treatment | ln Z | A1 / A2 / B | impact latitude 5 / 50 / 95 % |"); print("|---|---|---|---|")
    for d in T:
        a, c = A["cells"][d]["alone"], A["cells"][d]["comb"]
        fa = " / ".join(f"{a['imp']['families'][f]:.3f}" for f in ("A1", "A2", "B")); fc = " / ".join(f"{c['imp']['families'][f]:.3f}" for f in ("A1", "A2", "B"))
        qa = " / ".join(f"{x:.2f}" for x in a["imp"]["q05_q50_q95"]); qc = " / ".join(f"{x:.2f}" for x in c["imp"]["q05_q50_q95"])
        print(f"| {TN[d]} | {a['imp']['lnZ']:.3f} -> {c['imp']['lnZ']:.3f} | {fa} -> {fc} | {qa} -> {qc} |")


if __name__ == "__main__":
    if sys.argv[1] == "--compare": compare(sys.argv[2], sys.argv[3])
    else: main(sys.argv[1], sys.argv[2])

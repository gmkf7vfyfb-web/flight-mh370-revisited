"""Composer pass 1 (run C): markdown tables for the results note, from pass1-results.json and products-per-stratum.csv."""
import csv, json, pathlib, sys
out = pathlib.Path(sys.argv[1]); R = json.loads((out / "pass1-results.json").read_text())
rows = list(csv.DictReader(open(out / "products-per-stratum.csv")))
F = ["A1", "A2", "B"]
def f2(x): return "—" if x is None else f"{x:.2f}"
def lat(e): return f"{e['median']:.2f} ({e['q025']:.2f} to {e['q975']:.2f})"
L = []
for t, O in R["options"].items():
    L.append(f"\n#### {O['name']} — strata: {', '.join(O['strata'])}\n")
    sw = O["stratum_weights"]
    L.append("Stratum weights, 00:19-re-weighted (fixed): " + "; ".join(f"{s} {sw['reweighted-0019'][s]:.3f} ({sw['fixed'][s]:.3f})" for s in sw["fixed"]) + "\n")
    L.append("| product | " + " | ".join(f"{f}: P; median (95 %)" for f in F) + " | mixture: median (95 %) | 50 % / 90 % area (k km²) | > 212 m/s share | split-half overlap (1 partition) |")
    L.append("|---" * 8 + "|")
    for k in ("P1", "D", "G", "Ga", "Hn", "H", "Ha", "Hr5", "Gx", "Hx"):
        if k not in O["products"]:
            continue
        e = O["products"][k]["reweighted-0019"]
        cells = []
        for f in F:
            s = e["family_stats"].get(f)
            cells.append(f"{e['family_probability'][f]:.3f}; " + (lat(s) if s else "—"))
        L.append(f"| {k} | " + " | ".join(cells) + f" | {lat(e)} | {e['hdr50_area_km2']/1e3:.0f} / {e['hdr90_area_km2']/1e3:.0f} | {e['share_contact_speed_above_212']:.3f} | {e['split_half_overlap_one_partition']:.3f} |")
    L.append("")
    fx = O["products"]["G"]["fixed"]
    L.append(f"Fixed-weight mixture, G: median {lat(fx)}, 90 % area {fx['hdr90_area_km2']/1e3:.0f}k km²; H: {lat(O['products']['H']['fixed'])}, {O['products']['H']['fixed']['hdr90_area_km2']/1e3:.0f}k km².\n")
    # tension
    L.append("| tension of H against G | ln R (re-weighted / fixed) | 90 % HDR Jaccard | share of H's 90 % inside G's | mode displacement (NM) | mean displacement (NM) |")
    L.append("|---|---|---|---|---|---|")
    for p, T in O["tension"].items():
        lr = "not computed" if T["ln_R"] is None else f"{T['ln_R']:+.3f} / {T['ln_R_fixed']:+.3f}"
        L.append(f"| {p} | {lr} | {T['hdr90_jaccard']:.2f} | {T['share_of_H_hdr90_inside_G_hdr90']:.2f} | {T['mode_displacement_nm']:.0f} | {T['mean_displacement_nm']:.0f} |")
    ps = O["tension"]["before searches"]["per_stratum"]
    L.append("\nln R per stratum (before searches): " + "; ".join(f"{s} {v['ln_R']:+.3f} (seed range {min(v['ln_R_per_seed'].values()):+.2f} to {max(v['ln_R_per_seed'].values()):+.2f}; halves {v['ln_R_split_halves'][0]:+.3f} / {v['ln_R_split_halves'][1]:+.3f})" for s, v in ps.items()) + "\n")
    # evidence + ESS
    L.append("| product | ln-evidence vs flight + EoF (mixture, fixed strata) | per stratum | min effective parents per seed (per stratum) | not-computed weight, drift (max seed) |")
    L.append("|---|---|---|---|---|")
    for k in ("P1", "D", "Y", "S", "G", "Ga", "PE", "H", "Ha", "Hn", "Hr5", "PEr5"):
        if k not in O["evidence"]:
            continue
        ev = O["evidence"][k]; rr = [r for r in rows if r["option"] == O["name"] and r["product"] == k]
        ess = "; ".join(f"{r['stratum']} {float(r['min_ess_parents_per_seed']):,.0f}" for r in rr)
        nc = "; ".join(f"{float(r['not_computed_weight_max[debris-drift]']):.3f}" for r in rr if r.get("not_computed_weight_max[debris-drift]"))
        L.append(f"| {k} | {ev['ln_evidence_vs_P1_mixture']:+.3f} | " + "; ".join(f"{v:+.3f}" for v in ev["per_stratum_vs_P1"].values()) + f" | {ess} | {nc or '—'} |")
cov = list(csv.DictReader(open(out / "coverage-ess.csv")))
L.append("\n#### Coverage: effective impact rows (Kish, smallest seed), by family and latitude band\n")
L.append("| option | product | stratum | A1 | A2 | B | B code 3 / 5 | A code 4 | south of 39 S | 39-36 S | 36-33 S | 33-30 S | north of 30 S |")
L.append("|---" * 13 + "|")
for o in R["options"].values():
    for k in ("P1", "G", "Ga", "H", "Ha", "Hr5"):
        for st in o["strata"]:
            c = {(r["by"], r["value"]): r["min"] for r in cov if r["option"] == o["name"] and r["product"] == k and r["stratum"] == st}
            if not c: continue
            g = lambda by, v: f"{int(float(c.get((by, v), 0))):,}"
            L.append(f"| {o['name']} | {k} | {st} | {g('EoF family (family4_code)', 'A1')} | {g('EoF family (family4_code)', 'A2')} | {g('EoF family (family4_code)', 'B')} | "
                     f"{g('EoF family_code', '3')} / {g('EoF family_code', '5')} | {g('EoF family_code', '4')} | {g('impact latitude band', '-90.0..-39.0')} | {g('impact latitude band', '-39.0..-36.0')} | "
                     f"{g('impact latitude band', '-36.0..-33.0')} | {g('impact latitude band', '-33.0..-30.0')} | {g('impact latitude band', '-30.0..0.0')} |")
L.append("\n#### Contact speed above 212 m/s (1.25 VMO): share of each family's weight, all-rows products (removed in the 212 m/s version)\n")
L.append("| option | product | all | A1 | A2 | B |")
L.append("|---|---|---|---|---|---|")
for t, o in R["options"].items():
    if t.endswith("-v212"): continue
    for k in ("P1", "G", "H"):
        e = o["products"][k]["reweighted-0019"]; f = e["share_above_212_by_family"]
        L.append(f"| {o['name']} | {k} | {e['share_contact_speed_above_212']:.3f} | " + " | ".join(f2(f.get(x)) for x in F) + " |")
print("\n".join(L))

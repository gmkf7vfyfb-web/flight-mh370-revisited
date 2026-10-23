
_verdict2 = verdict
def verdict(c, d):
    if d["held"] and d["kind"] in ("imos","kadri") and d.get("p") is None and not (d["rx"] in c["rx"]):
        return "nm_nothing", f"held for {100*d['cover_frac']:.0f} % of the window but at the record edge, so no statistic"
    return _verdict2(c, d)
VC["nm_nothing"] = ("#f7f7f7", "Held: not scorable (no level model or record edge); nothing")
for c in cands:
    rows_ = ALLROWS[c["slug"]]
    if c is c10: draw_candidate(c10, rows_, f"{OUT}/{c10['slug']}", _a, _b, _f1, "\n".join(textwrap.wrap(_f2, 355)))
    else: draw_candidate(c, rows_, f"{OUT}/{c['slug']}", *texts_for3(c, rows_))
for rr in recs:
    c = next(x for x in cands if x["name"]==rr["candidate"]); d = next(x for x in ALLROWS[c["slug"]] if x["rx"]==rr["receiver"] and x["kind"]==rr["data_source"])
    rr["verdict_class"], rr["verdict"] = verdict(c, d)
MX = pd.DataFrame(recs); MX.to_csv(f"{OUT}/arrival_window_matrix.csv", index=False)
cnt = MX.verdict_class.value_counts().to_dict(); print(cnt)
exec(open("track_matrix.py").read())
print(sorted(os.listdir(OUT)))

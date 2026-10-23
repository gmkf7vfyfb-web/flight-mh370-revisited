
code = r'''
ROWS = [("H01W","kadri"),("H01W","royer"),("H08S","kadri"),("H08N","none"),("3315","imos"),("3376","imos"),("3274","imos"),("3275","imos"),("3250","imos"),
        ("NEAMS","none"),("SWAMS","royer"),("SSEIR","royer"),("MAD","royer"),("WKER","royer"),("NCRO","royer")]
ROW_LABEL = {("H01W","kadri"):"Cape Leeuwin (IMS H01W)\nKadri Fig. 9, digitised",("H01W","royer"):"Cape Leeuwin (IMS H01W)\nRoyer spectrogram, digitised",
  ("H08S","kadri"):"Diego Garcia South (IMS H08S)\nKadri Fig. 9, digitised",("H08N","none"):"Diego Garcia North\n(IMS H08N)",
  ("3315","imos"):"Perth Canyon logger 3315\nraw recording",("3376","imos"):"Perth Canyon logger 3376\nraw recording",
  ("3274","imos"):"Portland logger 3274\nraw recording",("3275","imos"):"Portland logger 3275\nraw recording",("3250","imos"):"Scott Reef logger 3250\nraw recording",
  ("NEAMS","none"):"OHASISBIO NEAMS",("SWAMS","royer"):"OHASISBIO SWAMS\nRoyer spectrogram, digitised",("SSEIR","royer"):"OHASISBIO SSEIR\nRoyer spectrogram, digitised",
  ("MAD","royer"):"OHASISBIO MAD\nRoyer spectrogram, digitised",("WKER","royer"):"OHASISBIO WKER\nRoyer spectrogram, digitised",("NCRO","royer"):"OHASISBIO NCRO\nRoyer spectrogram, digitised"}
NOT_HELD_REASON = {"H08N":"no recording obtained (IMS data not released to the project)", "NEAMS":"instrument lost on recovery: no data exist (Royer 2016 Table 1)"}
ROYER_ST = {"H01W":["H01W-2"],"SWAMS":["SWAMS-2","SWAMS-3"],"SSEIR":["SSEIR"],"MAD":["MAD"],"WKER":["WKER"],"NCRO":["NCRO"]}
PICK_ST = {"H01W":["H01W1","H01W2","H01W3"],"SWAMS":["SWAMS1","SWAMS2","SWAMS3"],"SSEIR":["SSEIR"],"MAD":["MAD"],"WKER":["WKER"],"NCRO":["NCRO"]}
PANEL_NULL = {"H01W": NULLS["3376"]["panel_H01W_M1b"], "H08S": NULLS["3376"]["panel_H08S_M1b"]}
def pval(s, null): return (np.sum(null >= s) + 1) / (len(null) + 1)
def thr(null): return {a: float(np.quantile(null, 1 - a)) for a in (0.3, 0.1, 0.05)}
def overlap(a0, a1, b0, b1): return max(0.0, min(a1, b1) - max(a0, b0))

def row_data(rx, kind, w0, w1, pad=120.0):
    s0, s1 = w0 - pad, w1 + pad; out = dict(rx=rx, kind=kind, w0=w0, w1=w1, s0=s0, s1=s1, held=False, cover=0.0, segs=[], picks=[])
    if kind == "none":
        out["reason"] = NOT_HELD_REASON[rx]; return out
    if rx in PICK_ST:
        pk = rarr[rarr.station.isin(PICK_ST[rx])]
        out["picks"] = [(T0 + float(r.arrival_s_after_T0), r.station, r.label if isinstance(r.label, str) else "", r.event_class) for _, r in pk.iterrows()
                        if s0 <= T0 + float(r.arrival_s_after_T0) <= s1]
    if kind == "imos":
        sel = rec[(rec.logger == rx) & (rec.t_end > s0) & (rec.t_start < s1)]
        null = NULLS[RS.NULL_STANDIN[rx]]["M1b"]; out["thr"] = thr(null); out["null_logger"] = RS.NULL_STANDIN[rx]
        best = None
        for i in sel.index:
            o = imos_record(i); out["segs"].append(o)
            out["cover"] += overlap(w0, w1, o["t0"], o["t0"] + len(o["x100_pa"]) / 100)
            tt = o["t0"] + o["m1b_t"]; m = (tt >= w0) & (tt <= w1)
            if m.any():
                j = np.argmax(np.where(m, o["m1b"], -np.inf))
                if best is None or o["m1b"][j] > best[0]: best = (float(o["m1b"][j]), float(tt[j]))
        out["bmed"] = M.bmed.get(rx, None)
        if out["bmed"] is None and out["segs"]:
            out["bmed"] = float(np.median(np.concatenate([s["lev"] for s in out["segs"]]))); out["bmed_note"] = "median of the records shown"
        if best: out["stat"], out["stat_t"] = best; out["p"] = pval(best[0], null)
    elif kind == "kadri":
        null = PANEL_NULL[rx]; out["thr"] = thr(null); best = None
        for p, v in PANELS.items():
            if v["st"] != rx: continue
            if v["t0"] + 600 < s0 or v["t0"] > s1: continue
            out["segs"].append(dict(panel=p, **v)); out["cover"] += overlap(w0, w1, v["t0"], v["t0"] + 600)
            tt = v["t0"] + v["m1b_t"]; m = (tt >= w0) & (tt <= w1)
            if m.any():
                j = np.argmax(np.where(m, v["m1b"], -np.inf))
                if best is None or v["m1b"][j] > best[0]: best = (float(v["m1b"][j]), float(tt[j]))
        if best: out["stat"], out["stat_t"] = best; out["p"] = pval(best[0], null)
    elif kind == "royer":
        best = None
        for r in ROY:
            if r["station"] not in ROYER_ST[rx]: continue
            if r["t"][-1] < s0 or r["t"][0] > s1: continue
            out["segs"].append(r); out["cover"] = max(out["cover"], overlap(w0, w1, r["t"][0], r["t"][-1]))
            bt = r["band"].t_utc_s.values + T0; bv = r["band"].psd_db_5_40.values; med = np.nanmedian(bv)
            m = (bt >= w0) & (bt <= w1) & np.isfinite(bv)
            if m.any():
                j = np.argmax(np.where(m, bv - med, -np.inf))
                if best is None or bv[j] - med > best[0]: best = (float(bv[j] - med), float(bt[j]), r["file"])
        if best: out["stat"], out["stat_t"], out["stat_file"] = best
    out["cover_frac"] = min(1.0, out["cover"] / max(w1 - w0, 1e-9))
    out["held"] = out["cover"] > 0
    if not out["held"]:
        if kind == "imos": out["reason"] = "no record overlaps the window (records are 307 s every 15 min" + (", alternating slots" if rx in ("3315","3376") else "") + ")"
        elif kind == "kadri": out["reason"] = "outside the published Kadri Fig. 9 panels (" + ("00:27-00:57" if rx == "H01W" else "01:00-01:20") + " UTC); raw data not held"
        else: out["reason"] = "no digitised Royer panel covers the window; raw data not held"
    return out
'''
open("track_rowdata.py","w").write(code); exec(code)
c = cands[0]
for rx, kind in ROWS:
    w0, _, w1 = c["win"][rx]; d = row_data(rx, kind, w0, w1)
    print(rx, kind, d["held"], round(d["cover_frac"],2), round(d.get("stat",np.nan),3), d.get("p"), hms(d["stat_t"]) if "stat_t" in d else "", len(d["picks"]), d.get("reason",""))

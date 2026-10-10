"""Stand-in helper (NOT module code): the IMOS event lists and scored coverage that enter L_hyd.

Runs the hydroacoustics module's own imos_coincidence.rec_events (unchanged, sha256 17376781...) on every MH370-day
recording of loggers 3315, 3376, 3274, 3275, with the module's stage A thresholds (3315 <- 3376, 3275 <- 3274) and
2b's pre-registered MH370 windows. Writes, per logger: the window, the scored segments (recording start + 32 s to
recording end, intersected with the window), every recorded segment of the day (scenario B), and the loose
(alpha 0.05) and strict (0.005) events inside the scored segments. Reads no impact sample.
Self-check: covered seconds must equal imos_coincidence.json 'descriptive_mh370_events' (372.5 / 450.5 / 350.5 / 550.1 s).
Usage: PYTHONPATH=<module>/prepare python extract_imos_events.py <out.json>
"""
import json, sys
import pandas as pd
import imos_coincidence as IC, imos_preregistration as P, imos_detectors as D

meta = P.parse_meta(); cal = IC.cal_for(meta)
thr_all = json.loads((IC.HERE / "results-data/stageA/summary_union.json").read_text())["thresholds"]
thr = {3376: thr_all["3376"], 3274: thr_all["3274"], 3315: thr_all["3376"], 3275: thr_all["3274"]}
mh = pd.read_csv(IC.HERE / "results-data/imos2b/mh370_windows.csv", parse_dates=["win_a", "win_b"])
win = {int(c): ((g.win_a.iloc[0] - D.DAY0).total_seconds(), (g.win_b.iloc[0] - D.DAY0).total_seconds()) for c, g in mh.groupby("logger")}
recs = pd.read_csv(IC.HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
out = {}
for cid in [3315, 3376, 3274, 3275]:
    a, b = win[cid]; segs, allsegs, evs = [], [], {"loose": [], "strict": []}
    for f in recs[recs.logger == cid].file:
        r = IC.rec_events(P.IMOS / f, cid, meta, cal, thr[cid])
        if r is None:
            continue
        s0, s1, ev = r; allsegs.append([s0 + 32, s1])
        lo, hi = max(s0 + 32, a), min(s1, b)
        if hi > lo:
            segs.append([lo, hi])
            for op in evs:
                evs[op] += [(t, v) for t, v in ev[op] if lo <= t <= hi]
    out[str(cid)] = dict(window=[a, b], scored_segments=segs, covered_s=sum(h - l for l, h in segs), recorded_segments=allsegs, events=evs)
open(sys.argv[1], "w").write(json.dumps(out, indent=1))
